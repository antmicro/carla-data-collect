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

    Output data are stored in CSV with header:
    ________________________________________
    | gx | gy | gz | ax | ay | az | anomaly |

    where:
        - g* are angular velocities read from gyroscope
        - a* are acceleration read from accelerometer
        - anomaly indicates whether anomaly has been detected

    IMUAnomalyDataset supports this strategies for anomaly detection:
    - Values of acceleration above arbitrary threshold
    are treated as anomalies.
    - Collisions with objects above arbitrary intensity
    values are treated as anomalies.
    - Sudden acceleration detection it is detected by sudden
    increase in throttle valve opening
    - Sudden braking detection it is detected by sudden
    increase of braking force.
    - Sudden steering wheel turns detection it is detected
    by sudden change of steering wheel angle

    For sudden acceleration, braking or steering wheel turns detection
    speed sensor and vehicle state sensor are required.

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
            A collision's intensity threshold used for anomalies detection.
        - detect_sudden_speeding: bool
            Enable sudden acceleration detection.
        - detect_sudden_braking: bool
            Enable sudden braking detection.
        - detect_sudden_steering: bool
            Enable sudden steering wheel turns detection.
        - speed_sensor_name: str
            Name of the speed sensor to read velocity value.
        - vehicle_state_sensor_name: str
            Name of vehicle state sensor to read basic
            vehicle state parameters.

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
        detect_sudden_speeding=False,
        detect_sudden_braking=False,
        detect_sudden_steering=False,
        speed_sensor_name: str = "speed",
        vehicle_state_sensor_name="vehicle",
        keystroke_sensor_name: str = "keys",
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
            Separator used by CSV files.
        sensor_imu_name : str
            Name of IMU sensor which data is used for dataset generation.
        accel_threshold : float
            Acceleration threshold above which reading is treated
            as an anomaly.
        sensor_collision_name : Optional[str]
            Name of optional collision sensor used for dataset generation.
        collision_intensity_threshold : float
            Collision intensity above which reading is treated as
            anomaly.
        detect_sudden_speeding : bool
            When set to true, sudden speeding is treated as
            anomalies.
        detect_sudden_braking : bool
            When set to true, sudden braking is treated as
            anomalies.
        detect_sudden_steering : bool
            When set to true, sudden steering wheel turns is treated as
            anomalies.
        speed_sensor_name : str
            Name of speed sensor from which speed value
            is retrieved.
        vehicle_state_sensor_name : str
            Name of vehicle state sensor from which basic
            data is collected.
        keystroke_sensor_name : str
            Name of keystroke sensor from which key events
            are collected.

        """
        super().__init__(input_path, output_path, sep)

        self._sensor_imu_name = sensor_imu_name
        self._sensor_collision_name = sensor_collision_name
        self._accel_threshold = accel_threshold
        self._collision_intensity_threshold = collision_intensity_threshold
        self._detect_sudden_speeding = detect_sudden_speeding
        self._detect_sudden_braking = detect_sudden_braking
        self._detect_sudden_steering = detect_sudden_steering
        self._speed_sensor_name = speed_sensor_name
        self._vehicle_state_sensor_name = vehicle_state_sensor_name
        self._keystroke_sensor_name = keystroke_sensor_name

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
        speed_data: Optional[pandas.DataFrame] = None,
        vehicle_data: Optional[pandas.DataFrame] = None,
        keystroke_data: Optional[pandas.DataFrame] = None,
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
        speed_data : Optional[pandas.DataFrame]
            Optional data frame with readings from
            speed sensor.
        vehicle_data : Optional[pandas.DataFrame]
            Optional data frame with basic vehicle
            state.
        keystroke_data : Optional[pandas.DataFrame]
            Optional readings from keyboards.

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

        detected_anomalies = 0

        if keystroke_data is not None:
            keystrokes = f"{self._keystroke_sensor_name}_keystrokes"

        if vehicle_data is not None:
            steering = f"{self._vehicle_state_sensor_name}_steer"
            throttle = f"{self._vehicle_state_sensor_name}_throttle"
            brake = f"{self._vehicle_state_sensor_name}_brake"

        if collision_data is not None:
            colided_with = f"{self._sensor_collision_name}_colided_with"
            colided_intensity = f"{self._sensor_collision_name}_intensity"
            max_collision_intensity = 0

        if speed_data is not None:
            speed_column = f"{self._speed_sensor_name}_speed"
            last_throttle_state = None
            last_braking_state = None
            last_steering_state = None
        anomalies = []

        timestamps = self.load_timestamps()

        for line_id, row in sensor_data.iterrows():
            a_x = row[accel_x]
            a_y = row[accel_y]
            a_z = row[accel_z]

            acceleration = math.sqrt(a_x * a_x + a_y * a_y + a_z * a_z)
            anomaly = 0

            keys_list = keystroke_data.loc[line_id, keystrokes]

            if "keydown_e" in keys_list:
                logging.debug(
                    f"Marked anomaly detected at timestamp {timestamps[line_id]}."
                )
                anomaly = 1

            if threshold != 0 and acceleration >= threshold:
                logging.debug(
                    f"Anomaly detect with threshold at index: {line_id} "
                )
                anomaly = 1

            if speed_data is not None:
                throttle_state = vehicle_data.loc[line_id, throttle]

                speed = float(speed_data.loc[line_id, speed_column]) * 3.6
                if speed > 5.0:
                    if last_throttle_state is None:
                        last_throttle_state = throttle_state
                    else:
                        delta_throttle = throttle_state - last_throttle_state

                        last_throttle_state = throttle_state

                        if delta_throttle >= 0.4:
                            logging.debug(
                                "Detected sudden acceleration "
                                f"at {timestamps[line_id]}."
                            )
                            anomaly = 1

                    if self._detect_sudden_braking:
                        brake_state = vehicle_data.loc[line_id, brake]

                        if last_braking_state is None:
                            last_braking_state = brake_state
                        else:
                            delta_braking = brake_state - last_braking_state

                            last_braking_state = brake_state

                            if delta_braking >= 0.4:
                                logging.debug(
                                    "Detected sudden braking "
                                    f"at {timestamps[line_id]} s."
                                )
                                anomaly = 1

                    if self._detect_sudden_steering:
                        steering_state = vehicle_data.loc[line_id, steering]

                        if last_steering_state is None:
                            last_steering_state = steering_state
                        else:
                            delta_steering = (
                                steering_state - last_steering_state
                            )

                            last_steering_state = steering_state

                            if abs(delta_steering) >= 0.4:
                                logging.debug(
                                    "Detected sudden steering"
                                    f"at {timestamps[line_id]} s."
                                )
                                anomaly = 1
                else:
                    last_throttle_state = None
                    last_braking_state = None
                    last_steering_state = None

            if collision_data is not None:
                obj_name = collision_data.loc[line_id, colided_with]
                intensity = float(
                    collision_data.loc[line_id, colided_intensity]
                )

                max_collision_intensity = max(
                    max_collision_intensity, intensity
                )

                if (
                    obj_name != "None"
                    and intensity >= self._collision_intensity_threshold
                ):
                    logging.debug(
                        f"Collision detected,with {obj_name} at index: {line_id}"
                    )
                    anomaly = 1

            if anomaly == 1:
                detected_anomalies += 1
            anomalies.append(anomaly)

        logging.info(f"Detected anomalies: {detected_anomalies}.")

        return anomalies

    def generate_dataset(self):
        imu_data = self.load_sensor_data(self._sensor_imu_name)
        collison_data = None
        speed_data = None
        vehicle_data = None
        keystroke_data = None

        if self._sensor_collision_name is not None:
            collison_data = self.load_sensor_data(self._sensor_collision_name)

        if (
            self._detect_sudden_speeding
            or self._detect_sudden_braking
            or self._detect_sudden_steering
        ):
            if self._speed_sensor_name is None:
                raise ValueError(
                    "Speed sensor is required for sudden acceleration,"
                    "steering turns and braking detection."
                )
            if self._vehicle_state_sensor_name is None:
                raise ValueError(
                    "Vehicle state sensor is required for sudden acceleration,"
                    "steering turns and braking detection."
                )

        if self._speed_sensor_name is not None:
            speed_data = self.load_sensor_data(self._speed_sensor_name)

        if self._keystroke_sensor_name is not None:
            keystroke_data = self.load_sensor_data(self._keystroke_sensor_name)

        if self._vehicle_state_sensor_name is not None:
            vehicle_data = self.load_sensor_data(
                self._vehicle_state_sensor_name
            )

        self.validate_sensor_data(imu_data)

        anomalies = self.detect_anomalies(
            sensor_data=imu_data,
            collision_data=collison_data,
            speed_data=speed_data,
            vehicle_data=vehicle_data,
            keystroke_data=keystroke_data,
        )

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
            "anomaly": anomalies,
        }

        with open(self.get_output_path(), "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))
