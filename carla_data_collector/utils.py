# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Module with helper functions.
"""

import logging
import re
from typing import List

import carla


def get_list_of_docs_objects() -> List[str]:
    """
    Get list of implemented sensors
    and datasets.

    Returns
    -------
    List[str]
        Names of implemented datasets and
        sensors.

    """
    from carla_data_collector.datasets import __all__ as datasets
    from carla_data_collector.sensors import __all__ as sensors

    return [*datasets, *sensors]


def find_weather_presets() -> List[str]:
    """
    Returns weather presets.

    Returns
    -------
    List[str]
        Found weather presets.

    """
    find_words_pattern = (
        r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)"
    )

    def name(x):
        return " ".join(m.group(0) for m in re.finditer(find_words_pattern, x))

    presets = [
        x for x in dir(carla.WeatherParameters) if re.match("[A-Z].+", x)
    ]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor: carla.Actor, truncate: int = 250) -> str:
    """
    Get actor display name.

    Parameters
    ----------
    actor : carla.Actor
        Actor to get name from.
    truncate : int
        Maximum name length

    Returns
    -------
        Display name of provided actor.

    """
    name = " ".join(actor.type_id.replace("_", ".").title().split(".")[1:])
    return (name[: truncate - 1] + "\u2026") if len(name) > truncate else name


def get_actor_blueprints(
    world: carla.World, filter: str, generation: str
) -> List[carla.ActorBlueprint]:
    """
    Get actor blueprints matching pattern.

    Parameters
    ----------
    world : carla.World
        Object representing Carla's simulation.
    filter : str
        Filter pattern.
    generation : str
        Generation id to select, when 'all' is passed
        all generations is selected.

    """
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2, 3]:
            bps = [
                x
                for x in bps
                if int(x.get_attribute("generation")) == int_generation
            ]
            return bps
        else:
            raise ValueError()
    except Exception:
        logging.warning(
            "Actor Generation is not valid. No actor will be spawned."
        )
        return []


def clamp(min_value: float, max_value: float, value: float) -> float:
    """
    Clamp provided value between min and max value.

    Parameters
    ----------
    min_value : float
        Minimum value.
    max_value : float
        Maximum value.
    value : float
        Value to clamp.

    Returns
    -------
    float
        Clamped value.

    """
    return max(min_value, min(value, max_value))
