# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
A script for generating mini spot dataset.
"""

import csv
import logging
import math
import re
from pathlib import Path
from typing import List, Optional, Union

import pandas

from carla_data_collector.datasets.base import Dataset


class IMUAnomalyDataset(Dataset):
    """
    IMUAnomalyDataset is anomaly dataset generator
    based on IMU sensor's readings.

    Output data are store in CSV with header:
    ________________________________________
    | gx | gy | gz | ax | ay | az | anomaly |

    where:
        - g* are angular velocities read from gyroscope
        - a* are accleration read from acclerometer
        - anomaly indicateds whether anomaly has been detected

    IMUAnomalyDataset supports this strategies for anomaly detection:
    - Values of acceleration above arbitrary threshold
    are treated as anomalies.
    - Collisions with objects above arbitary intensity
    value are treated as anomalies.

    Supported attributes:
        - output_path: str
            A path to an output dataset.
        - sep: str
            Separator used by output CSV files,
            ',' by default.
        - sensor_imu_name: str
            Name of an IMU sensor to get data from.
        - accel_threshold: float
            An acceleration threshold used for anomalies detection.
        - sensor_collision_name: str
            Optional name for collision sensor.
        - collision_intensity_threshold: float
            A collisions's intensity threshold used for anomalies detection.
    """

    def __init__(
        self,
        input_path: Union[Path, str],
        output_path: Union[Path, str],
        sep: str = ";",
        sensor_imu_name: str = None,
        accel_threshold: float = 20.0,
        sensor_collision_name: Optional[str] = None,
        collision_intensity_threshold: float = 1000.0,
    ):
        """
        Initialize IMUAnomalyDataset dataset.

        Parameters
        ----------
        input_path : Union[Path,str]
            Path to CSV file with raw data readings.
        output_path : Union[Path,str]
            Path to CSV file with generated dataset.
        sep : str
            Seperator used by CSV files.
        sensor_imu_name : str
            Name of IMU sensor which data is used for dataset generation.
        accel_threshold : float
            Acceleration threshold above which reading is treated
            as anomaly.
        sensor_collision_name : Optional[str]
            Name of optional collision sensor used for dataset generation.
        collision_intensity_threshold : float
            Collision intensity above which reading is treated as
            anomaly.

        """
        super().__init__(input_path, output_path, sep)

        self._sensor_imu_name = sensor_imu_name
        self._sensor_collision_name = sensor_collision_name
        self._accel_threshold = accel_threshold
        self._collision_intensity_threshold = collision_intensity_threshold

    def validate_sensor_data(self, data: pandas.DataFrame):
        """
        Function used for validating data from
        necessary sensors.

        Parameters
        ----------
        data : pandas.DataFrame
            Data frame with sensor's data.

        Raises
        ------
        ValueError
            Raised when sensor data are invalid.

        """
        columns = data.columns

        required_columns = [
            "accel_x",
            "accel_y",
            "accel_z",
            "gyro_x",
            "gyro_y",
            "gyro_z",
            "compas",
        ]

        if len(columns) != len(required_columns):
            raise ValueError("Column count mismatch.")

        expression = rf"^{self._sensor_imu_name}_"

        for index in columns:
            value_name = re.sub(expression, "", index)
            if value_name not in required_columns:
                raise ValueError(f"Missing property {value_name}.")

    def detect_anomalies(
        self,
        sensor_data: pandas.DataFrame,
        collision_data: Optional[pandas.DataFrame] = None,
    ) -> List[int]:
        """
        Detects anomalies in input data.

        Parameters
        ----------
        sensor_data : pandas.DataFrame
            Data frame with readings from IMU.
        collision_data : Optional[pandas.DataFrame]
            Optional data frame with readings from
            collision sensor.

        Returns
        -------
        List[int]
            List with detection results for each row.
            1 indicates anomaly and 0 does not.

        """
        threshold = self._accel_threshold
        sensor_name = self._sensor_imu_name
        accel_x = f"{sensor_name}_accel_x"
        accel_y = f"{sensor_name}_accel_y"
        accel_z = f"{sensor_name}_accel_z"

        if collision_data is not None:
            colided_with = f"{self._sensor_collision_name}_colided_with"
            colided_intensity = f"{self._sensor_collision_name}_intensity"

        anomalies = []

        for id, row in sensor_data.iterrows():
            a_x = row[accel_x]
            a_y = row[accel_y]
            a_z = row[accel_z]

            acceleration = math.sqrt(a_x * a_x + a_y * a_y + a_z * a_z)
            anomaly = 0

            if threshold != 0 and acceleration >= threshold:
                logging.debug(f"Anomaly detect with threshold at index: {id} ")
                anomaly = 1

            if collision_data is not None:
                obj_name = collision_data.loc[id, colided_with]
                intensity = float(collision_data.loc[id, colided_intensity])

                if (
                    obj_name != "None"
                    and intensity >= self._collision_intensity_threshold
                ):
                    logging.debug(
                        f"Collision detected,with {obj_name} at index: {id}"
                    )
                    anomaly = 1

            anomalies.append(anomaly)

        return anomalies

    def generate_dataset(self):
        imu_data = self.load_sensor_data(self._sensor_imu_name)
        collison_data = None

        if self._sensor_collision_name is not None:
            collison_data = self.load_sensor_data(self._sensor_collision_name)

        self.validate_sensor_data(imu_data)

        anoamlies = self.detect_anomalies(imu_data, collison_data)

        accel_x = f"{self._sensor_imu_name}_accel_x"
        accel_y = f"{self._sensor_imu_name}_accel_y"
        accel_z = f"{self._sensor_imu_name}_accel_z"

        gyro_x = f"{self._sensor_imu_name}_gyro_x"
        gyro_y = f"{self._sensor_imu_name}_gyro_y"
        gyro_z = f"{self._sensor_imu_name}_gyro_z"

        data = {
            "gx": imu_data[gyro_x],
            "gy": imu_data[gyro_y],
            "gz": imu_data[gyro_z],
            "ax": imu_data[accel_x],
            "ay": imu_data[accel_y],
            "az": imu_data[accel_z],
            "anomaly": anoamlies,
        }

        # Detect anomalies
        mini_spot = pandas.DataFrame(data)

        mini_spot.to_csv(self.get_output_path(), sep=self._sep, index=False)
        
        with open(self.get_output_path(), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
