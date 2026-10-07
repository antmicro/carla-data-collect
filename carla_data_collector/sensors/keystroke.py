# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for keystroke recoder handler.
"""

import weakref
from typing import TYPE_CHECKING, Optional

import carla

from carla_data_collector.sensors.base import Base

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class KeyStrokeSensor(Base):
    """Dummy sensor used for collecting keystrokes from user."""

    def __init__(
        self,
        name: str,
        parent_actor: carla.Actor,
        transform: Optional[carla.Transform] = None,
        **kwargs: dict,
    ):
        """
        Class for reading keyboard events.

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
        super().__init__(name, parent_actor, "", transform, **kwargs)

    def get_data(self, world: "World"):
        world.collects_events = True
        keystrokes = world.get_last_events()
        return {"keystrokes": keystrokes}

    @staticmethod
    def _callback(weak_self: weakref.ReferenceType, event: object):
        pass
