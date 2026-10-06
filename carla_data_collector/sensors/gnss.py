# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for GNSS sensor handler.
"""

import carla

from carla_data_collector.sensors.base import Base

class GnssSensor(Base):
    """
    GNSS sensor handler.
    """
    
    def __init__(self,name, parent_actor,transform = None, **kwargs):
        self.sensor = None
        self.lat = 0.0
        self.lon = 0.0
        
        transform = carla.Transform(carla.Location(x=1.0, z=2.8)) if transform is None else transform
        
        super().__init__(name, parent_actor,'sensor.other.gnss',transform,**kwargs)

    @staticmethod
    def _callback(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude
    
    def get_data(self, world):
        return {
            "lat": self.lat,
            "lon": self.lon
        }
