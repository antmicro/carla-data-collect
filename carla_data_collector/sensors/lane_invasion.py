# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for lane invasion sensor.
"""

import weakref
from typing import TYPE_CHECKING, Optional

import carla

from carla_data_collector.sensors.base import Base

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class LaneInvasionSensor(Base):
    """Lane invasion sensor handler."""

    def __init__(
        self,
        name: str,
        parent_actor: carla.Actor,
        transform: Optional[carla.Transform] = None,
        **kwargs: dict,
    ):
        """
        Class for reading data from lane invasion sensor.

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
        self.lane_types = set([])
        # If the spawn object is not a vehicle,
        # we cannot use the Lane Invasion Sensor
        if parent_actor.type_id.startswith("vehicle."):
            self.hud = kwargs["hud"]
            transform = carla.Transform() if transform is None else transform

            super().__init__(
                name,
                parent_actor,
                "sensor.other.lane_invasion",
                transform,
                **kwargs,
            )

    def get_data(self, world: "World"):
        lane_types = list(self.lane_types)
        self.lane_types = set([])
        return {"crossed_lines": lane_types}

    @staticmethod
    def _callback(
        weak_self: weakref.ReferenceType, event: carla.LaneInvasionEvent
    ):
        self = weak_self()
        if not self:
            return
        self.lane_types = set(x.type for x in event.crossed_lane_markings)
        text = [f"{str(x).split()[-1]}" for x in self.lane_types]
        self.hud.notification(f"Crossed line {' and '.join(text)}")
