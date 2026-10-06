# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Base class for sensors.
"""

import weakref
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import carla

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class Base(ABC):
    """
    Base class for sensors,
    """

    def __init__(
        self,
        name: str,
        parent_actor: carla.Actor,
        blue_print: str,
        transform: carla.Transform,
        **kwargs: dict,
    ):
        """
        Base class for sensor initialization.

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
        self.sensor = None
        self.name = name
        self._parent = parent_actor
        world = self._parent.get_world()

        if len(blue_print) != 0:
            bp = world.get_blueprint_library().find(blue_print)

            for attr in bp:
                if attr.id in kwargs and attr.is_modifiable:
                    bp.set_attribute(attr.id, str(kwargs[attr.id]))

            self.sensor = world.spawn_actor(
                bp, transform, attach_to=self._parent
            )

            weak_self = weakref.ref(self)
            self.sensor.listen(lambda data: self._callback(weak_self, data))

    @abstractmethod
    def get_data(self, world: "World"):
        """
        Get data collected by sensor.

        Parameters
        ----------
        world : World
            Simulation world used to get
            additional data.

        """
        pass

    @staticmethod
    @abstractmethod
    def _callback(weak_self: weakref.ReferenceType, data: object):
        """
        Carla's sensor callback used
        to collect data.

        Parameters
        ----------
        weak_self : weakref.ReferenceType
            Weak reference to class object.
        data : object
            Object with sensory data.

        """
        pass
