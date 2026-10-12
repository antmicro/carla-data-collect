# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for vehicle state handler.
"""

import weakref
from typing import TYPE_CHECKING, Optional

import carla

from carla_data_collector.sensors.base import Base

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class VehicleStateSensor(Base):
    """
    General vehicle state handler, which gives data about:
    - steering wheel position
    - throttle position
    - brake pedal position
    - selected gear
    - hand brake state.

    """

    def __init__(
        self,
        name: str,
        parent_actor: carla.Actor,
        transform: Optional[carla.Transform] = None,
        **kwargs: dict,
    ):
        """
        Class for handling basic vehicle state.

        Parameters
        ----------
        name : str
            Name of the sensor.
        parent_actor : carla.Actor
            Carla's actor to whom sensor is attached.
        blue_print : str
            Carla's blue print name of the sensor.
        transform: carla.Transfrom
            Translation and rotation of the sensor.
        **kwargs : dict
            Additonal parameters.

        """
        super().__init__(name, parent_actor, "", transform, **kwargs)

    def get_data(self, world: "World"):
        control = self._parent.get_control()

        return {
            "throttle": control.throttle,
            "steer": control.steer,
            "brake": control.brake,
            "handbrake": control.hand_brake,
            "gear": control.gear,
            "reverse": control.reverse,
            "manual_mode": control.manual_gear_shift,
        }

    @staticmethod
    def _callback(weak_self: weakref.ReferenceType, event: object):
        pass
