# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides handlers for various sensors supported by Carla.
"""

from carla_data_collector.sensors.collision import CollisionSensor
from carla_data_collector.sensors.gnss import GnssSensor
from carla_data_collector.sensors.imu import IMUSensor
from carla_data_collector.sensors.keystroke import KeyStrokeSensor
from carla_data_collector.sensors.lane_invasion import LaneInvasionSensor
from carla_data_collector.sensors.radar import RadarSensor
from carla_data_collector.sensors.speed import SpeedSensor
from carla_data_collector.sensors.vehicle_state import VehicleStateSensor

__all__ = [
    "CollisionSensor",
    "GnssSensor",
    "IMUSensor",
    "KeyStrokeSensor",
    "LaneInvasionSensor",
    "RadarSensor",
    "SpeedSensor",
    "VehicleStateSensor"
]
