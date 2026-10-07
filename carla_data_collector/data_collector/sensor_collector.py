# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementation for sensor data collector.
"""

import csv
from pathlib import Path
from typing import List, Union

from carla_data_collector.world.world import World


class SensorCollector:
    """
    Data collector for collecting and saving data to CSV file.
    """

    def __init__(self, output_path: Union[Path, str], world: World):
        """
        Sensor collector initialization.

        Parameters
        ----------
        output_path : Path
            Output CSV path.
        world : World
            Simulation world used to get
            additional data.

        """
        self._output_path = Path(output_path)
        self._world = world
        self._file = None
        self._writer = None
        self._start_time = None
        self._last_frame = None
        self._header = self._generate_header()

    def start(self):
        """
        Initialize output CSV file with
        sensor readings.
        """
        self._file = open(self._output_path, "w")

        self._writer = csv.writer(self._file, delimiter=";")
        self._writer.writerow(self._header)

    def record(self, timestamp: float, frame: int):
        """
        Collect and save data from sensors
        registered in simulation.

        Parameters
        ----------
        timestamp : float
            Elapsed time from simulation start
            in seconds.
        frame : int
            Current simulation frame id.

        """
        if self._start_time is None:
            self._start_time = timestamp
        if self._last_frame == frame:
            return
        self._last_frame = frame

        sensors = self._world.sensors
        data = [timestamp - self._start_time]

        for sensor in sensors:
            for _, val in sensor.get_data(self._world).items():
                data.append(val)

        self._writer.writerow(data)

    def stop(self):
        """Stop collecting data."""
        self._file.close()

    def _generate_header(self) -> List[str]:
        """
        Generates CSV header.

        Returns
        -------
        List[str]
            List with columns name.

        """
        sensors = self._world.sensors

        header = ["timestamp"]

        for sensor in sensors:
            name = sensor.name
            for attr in sensor.get_data(self._world).keys():
                header.append(f"{name}_{attr}")

        return header
