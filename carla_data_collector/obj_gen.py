# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Script used to get sensors or datasets class from class name.
"""

import carla_data_collector.datasets as datasets
import carla_data_collector.sensors as sensors


def get_sensor_from_name(name: str) -> type:
    """
    Returns sensor class with provided name.

    Parameters
    ----------
    name : str
        Name of class.

    Returns
    -------
    type
        Class implementation.

    """
    if name in sensors.__all__:
        return getattr(sensors, name)

    raise ValueError(f"No sensor {name} avaliable.")


def get_dataset_from_name(name: str) -> type:
    """
    Returns dataset class with provided name.

    Parameters
    ----------
    name : str
        Name of class.

    Returns
    -------
    type
        Class implementation.

    """
    if name in datasets.__all__:
        return getattr(datasets, name)

    raise ValueError(f"No dataset {name} avaliable.")


def get_object_from_name(name: str) -> type:
    """
    Returns class with provided name.

    Parameters
    ----------
    name : str
        Name of class.

    Returns
    -------
    object
        Class implementation.

    """
    if name in sensors.__all__:
        return get_sensor_from_name(name)

    if name in datasets.__all__:
        return get_dataset_from_name(name)

    raise ValueError(f"Class with name {name} not found.")
