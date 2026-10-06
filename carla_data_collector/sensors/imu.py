# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for IMU sensor handler.
"""

import math

import carla

from carla_data_collector.sensors.base import Base

class IMUSensor(Base):
    """
    IMU sensor handler.
    """
    
    def __init__(self,name, parent_actor, transform = None, **kwargs):
        self.sensor = None
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        
        transform = carla.Transform() if transform is None else transform
        
        super().__init__(name, parent_actor,'sensor.other.imu',transform, **kwargs)

    @staticmethod
    def _callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.compass = math.degrees(sensor_data.compass)
        
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
