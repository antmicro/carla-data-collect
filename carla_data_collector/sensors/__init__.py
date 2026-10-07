# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides handlers for various sensors supported by Carla.
"""

from carla_data_collector.sensors.collision import CollisionSensor
from carla_data_collector.sensors.gnss import GnssSensor
from carla_data_collector.sensors.imu import IMUSensor
from carla_data_collector.sensors.lane_invasion import LaneInvasionSensor
from carla_data_collector.sensors.radar import RadarSensor
from carla_data_collector.sensors.speed import SpeedSensor
from carla_data_collector.sensors.keystroke import KeyStrokeSensor

__all__ = [
    "CollisionSensor",
    "GnssSensor",
    "IMUSensor",
    "LaneInvasionSensor",
    "RadarSensor",
    "SpeedSensor",
    "VehicleStateSensor",
    "KeyStrokeSensor"
]
