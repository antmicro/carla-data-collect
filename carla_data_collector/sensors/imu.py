# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for IMU sensor handler.
"""

import math
import weakref
from typing import TYPE_CHECKING, Optional

import carla

from carla_data_collector.sensors.base import Base
from carla_data_collector.utils import clamp

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class IMUSensor(Base):
    """
    IMU sensor handler.

    Avaliable attributes:
    - accelerometer_limits: float
        A maximum value of acceleration readings from IMU,
        99 by default.
    - gyroscope_limits: float
        A maximum value of gyroscope readings from IMU,
        99 by default.
    - noise_accel_stddev_x: float
        Standard deviation parameter in the noise model
        for acceleration (X axis).
    - noise_accel_stddev_y: float
        Standard deviation parameter in the noise
        model for acceleration (Y axis).
    - noise_accel_stddev_z: float
        Standard deviation parameter in the noise
        model for acceleration (Z axis).
    - noise_gyro_bias_x: float
        Mean parameter in the noise model
        for the gyroscope (X axis).
    - noise_gyro_bias_y: float
        Mean parameter in the noise model
        for the gyroscope (Y axis).
    - noise_gyro_bias_z: float
        Mean parameter in the noise model
        for the gyroscope (Z axis).
    - noise_gyro_stddev_x: float
        Standard deviation parameter in the noise
        model for the gyroscope (X axis).
    - noise_gyro_stddev_y: float
        Standard deviation parameter in the noise
        model for the gyroscope (Y axis).
    - noise_gyro_stddev_Z: float
        Standard deviation parameter in the noise
        model for the gyroscope (Z axis).
    - noise_seed: int
        Initializer for a pseudorandom number generator.
    - sensor_tick: float
        Simulation seconds between sensor captures (ticks).
    """

    def __init__(
        self,
        name: str,
        parent_actor: carla.Actor,
        transform: Optional[carla.Transform] = None,
        **kwargs: dict,
    ):
        """
        Class for reading data from IMU sensor.

        Parameters
        ----------
        name : str
            Name of the sensor.
        parent_actor : carla.Actor
            Carla's actor to whom sensor is attached.
        transform: Optional[carla.Transfrom]
            Translation and rotation of the sensor.
        **kwargs : dict
            Additonal parameters.

        """
        self.sensor = None
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        self.accelerometer_limits = kwargs.get("accelerometer_limit", 99.9)
        self.gyroscope_limits = kwargs.get("gyroscope_limits", 99.9)

        transform = carla.Transform() if transform is None else transform

        super().__init__(
            name, parent_actor, "sensor.other.imu", transform, **kwargs
        )

    def get_data(self, world: "World"):
        return {
            "accel_x": self.accelerometer[0],
            "accel_y": self.accelerometer[1],
            "accel_z": self.accelerometer[2],
            "gyro_x": self.gyroscope[0],
            "gyro_y": self.gyroscope[1],
            "gyro_z": self.gyroscope[2],
            "compas": self.compass,
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
