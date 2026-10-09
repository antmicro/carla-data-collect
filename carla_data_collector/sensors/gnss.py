# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for GNSS sensor handler.
"""

import weakref
from typing import TYPE_CHECKING, Optional

import carla

from carla_data_collector.sensors.base import Base

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class GnssSensor(Base):
    """
    GNSS sensor handler.

    Avaliable attributes:
    - noise_alt_bias: float
        Mean parameter in the noise model for altitude.
    - noise_alt_stddev: float
        Standard deviation parameter in the noise model for altitude.
    - noise_lat_bias: float
        Mean parameter in the noise model for latitude.
    - noise_lat_stddev: float
        Standard deviation parameter in the noise model for latitude.
    - noise_lon_bias: float
        Mean parameter in the noise model for longitude.
    - noise_lon_stddev: float
        Standard deviation parameter in the noise model for longitude.
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
        Class for reading data from GNSS sensor.

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
        self.lat = 0.0
        self.lon = 0.0

        transform = (
            carla.Transform(carla.Location(x=1.0, z=2.8))
            if transform is None
            else transform
        )

        super().__init__(
            name, parent_actor, "sensor.other.gnss", transform, **kwargs
        )

    def get_data(self, world: "World"):
        return {"lat": self.lat, "lon": self.lon}

    @staticmethod
    def _callback(
        weak_self: weakref.ReferenceType, event: carla.GnssMeasurement
    ):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude
