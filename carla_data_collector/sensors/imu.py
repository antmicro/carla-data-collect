# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for IMU sensor handler.
"""

import math
import weakref

import carla

from carla_data_collector.sensors.base import Base
from carla_data_collector.utils import clamp

class IMUSensor(Base):
    """
    IMU sensor handler.
    """
    
    def __init__(self,name, parent_actor, transform = None, **kwargs):
        self.sensor = None
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        self.accelerometer_limits = kwargs.get('accelerometer_limit',99.9)
        self.gyroscope_limits = kwargs.get('gyroscope_limits',99.9)
        
        transform = carla.Transform() if transform is None else transform
        
        super().__init__(name, parent_actor,'sensor.other.imu',transform, **kwargs)

    def get_data(self, world):
        return {
            "accel_x": self.accelerometer[0],
            "accel_y": self.accelerometer[1],
            "accel_z": self.accelerometer[2],
            "gyro_x": self.gyroscope[0],
            "gyro_y": self.gyroscope[1],
            "gyro_z": self.gyroscope[2],
            "compas": self.compass
        }

    @staticmethod
    def _callback(
        weak_self: weakref.ReferenceType, sensor_data: carla.IMUMeasurement
    ):
        self = weak_self()
        if not self:
            return
        limits = (-self.accelerometer_limits, self.accelerometer_limits)
        self.accelerometer = (
            clamp(limits[0], limits[1], sensor_data.accelerometer.x),
            clamp(limits[0], limits[1], sensor_data.accelerometer.y),
            clamp(limits[0], limits[1], sensor_data.accelerometer.z),
        )
        limits = (-self.gyroscope_limits, self.gyroscope_limits)
        self.gyroscope = (
            clamp(limits[0], limits[1], sensor_data.gyroscope.x),
            clamp(limits[0], limits[1], sensor_data.gyroscope.y),
            clamp(limits[0], limits[1], sensor_data.gyroscope.z),
        )
        self.compass = math.degrees(sensor_data.compass)
