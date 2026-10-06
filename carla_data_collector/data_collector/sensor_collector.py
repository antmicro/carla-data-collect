# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for sensor data collector.
"""

from pathlib import Path
import threading
import time

from carla_data_collector.world.world import World

class SensorCollector:
    """
    Data collector for collecting and saving data to CSV file.
    """
    
    def __init__(
        self,
        output_path: Path,
        timestamp: float,
        world: World
    ):
        self._output_path = output_path
        self._world = world
        self._file = None
        self._thread = None
        self._timestamp = timestamp
        self._running = False
        self._ticks = 0.0
        
    def _collector_loop(self):
        while self._running:
            self.record()
            time.sleep(self._timestamp)
        
    def start_thread(self):
        self.start()
        self._running = True
        self._thread = threading.Thread(target=self._collector_loop)
        self._thread.start()
        
    def start(self):
        self._file = open(self._output_path, "w")
        # In the future it will be based on defined sensors
        print("timestamp,brake,handbrake,acc_x,acc_y,acc_z", file=self._file)
        
    def record(self):
        c = self._world.player.get_control()
        accel = self._world.imu_sensor.accelerometer
        print(self._ticks, float(c.brake), float(c.hand_brake), *accel, sep=",", file=self._file)
        self._ticks += self._timestamp
    
    def stop(self):
        self._running = False
        self._file.close()