# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for collsion sensor handler.
"""

import math
import weakref
from typing import TYPE_CHECKING, Optional

import carla

from carla_data_collector.sensors.base import Base
from carla_data_collector.utils import get_actor_display_name

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class CollisionSensor(Base):
    """Collsion sensor handler."""

    def __init__(
        self,
        name: str,
        parent_actor: carla.Actor,
        transform: Optional[carla.Transform] = None,
        **kwargs: dict,
    ):
        """
        Class for reading data from collision sensor.

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
        self.intensity = 0
        self.colided_with = "None"
        self.hud = kwargs["hud"]
        transform = carla.Transform() if transform is None else transform

        super().__init__(
            name, parent_actor, "sensor.other.collision", transform, **kwargs
        )

    def get_data(self, world: "World"):
        intensity = self.intensity
        colided_with = self.colided_with

        self.intensity = 0
        self.colided_with = "None"
        return {"intensity": intensity, "colided_with": colided_with}

    @staticmethod
    def _callback(
        weak_self: weakref.ReferenceType, event: carla.CollisionEvent
    ):
        self = weak_self()
        if not self:
            return
        actor_type = get_actor_display_name(event.other_actor)
        self.hud.notification(f"Collision with {actor_type}")
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.colided_with = actor_type
        self.intensity = intensity
