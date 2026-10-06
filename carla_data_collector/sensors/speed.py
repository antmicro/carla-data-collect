# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for Speed sensor handler.
"""

import math
import weakref
from typing import TYPE_CHECKING, Optional

import carla

from carla_data_collector.sensors.base import Base

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class SpeedSensor(Base):
    """Speed sensor handler."""

    def __init__(
        self,
        name: str,
        parent_actor: carla.Actor,
        transform: Optional[carla.Transform] = None,
        **kwargs: dict,
    ):
        """
        Class for reading data from speed sensor.

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

        velocity = self._parent.get_velocity()

        speed = math.sqrt(
            velocity.x * velocity.x
            + velocity.y * velocity.y
            + velocity.z * velocity.z
        )

        return {"speed": speed}

    @staticmethod
    def _callback(weak_self: weakref.ReferenceType, event: object):
        pass
