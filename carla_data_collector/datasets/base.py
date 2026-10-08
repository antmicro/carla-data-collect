# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Base class for dataset.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

import pandas


class Dataset(ABC):
    """Base class for dataset generation."""

    def __init__(
        self,
        input_path: Union[Path, str],
        output_path: Union[Path, str],
        sep: str = ";",
    ):
        """
        Initialize Dataset.

        Parameters
        ----------
        input_path : Union[Path,str]
            Path to CSV file with raw data readings.
        output_path : Union[Path,str]
            Path to CSV file with generated dataset.
        sep : str
            Seperator used by CSV files.

        """
        super().__init__()
        self._filepath = Path(input_path)
        self._output_path = Path(output_path)
        self._sep = sep
        self._data = None
        self._load_data_file()

    def get_output_path(self) -> Path:
        """
        Returns path to generated dataset.

        Returns
        -------
        Path
            Path to generated dataset.

        """
        return self._output_path

    def load_timestamps(self) -> pandas.DataFrame:
        """
        Returns column with timestamp.

        Returns
        -------
        pandas.DataFrame
            DataFrame with timestamp column.

        """
        return self._data["timestamp"]

    def load_sensor_data(self, name: str) -> pandas.DataFrame:
        """
        Find all sensor data, from sensor with
        selected name.

        Parameters
        ----------
        name : str
            Name of the sensor.

        Returns
        -------
        pandas.DataFrame
            DataFrame with sensor's data.

        """
        rule = re.compile(rf"^{name}")

        columns_keys = self._data.columns

        found_keys = list(filter(rule.match, columns_keys))

        data_to_return = self._data[found_keys]

        return data_to_return

    @abstractmethod
    def generate_dataset(self):
        """Function for dataset generation."""

    def _load_data_file(self):
        """
        Function for loading CSV with sensor's data.
        """
        self._data = pandas.read_csv(
            self._filepath,
            sep=";",
            keep_default_na=False,
            na_values=["NaN"],
        )
