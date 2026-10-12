# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Main application script.
"""

import argparse
import logging
from typing import List, Tuple

import carla
import pygame
import yaml

from carla_data_collector.control.keyboard import KeyboardControl
from carla_data_collector.data_collector.sensor_collector import (
    SensorCollector,
)
from carla_data_collector.hud.hud import HUD
from carla_data_collector.obj_gen import (
    get_dataset_from_name,
    get_object_from_name,
)
from carla_data_collector.utils import get_list_of_docs_objects
from carla_data_collector.world.world import World


def game_loop(args: argparse.Namespace):
    """
    Handle simulation mode.

    Parameters
    ----------
    args : argparse.Namespace
        Input arguments.

    """
    pygame.init()
    pygame.font.init()
    args.width, args.height = [int(x) for x in args.res.split("x")]
    world = None
    original_settings = None

    output_path = args.output

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2000.0)
        timestamp = 1.0 / float(args.sample_rate)

        sim_world = client.get_world()
        if args.sync:
            original_settings = sim_world.get_settings()
            settings = sim_world.get_settings()
            if not settings.synchronous_mode:
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = timestamp
            sim_world.apply_settings(settings)

            traffic_manager = client.get_trafficmanager()
            traffic_manager.set_synchronous_mode(True)

        if args.autopilot and not sim_world.get_settings().synchronous_mode:
            logging.warning(
                "You are currently in asynchronous mode and could "
                "experience some issues with the traffic simulation"
            )

        display = pygame.display.set_mode(
            (args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        display.fill((0, 0, 0))
        pygame.display.flip()

        help_str = KeyboardControl.help_str()

        hud = HUD(args.width, args.height, help_str)
        world = World(sim_world, hud, args)
        controller = KeyboardControl(world, args.autopilot)

        logging.info(help_str)

        collector = SensorCollector(output_path=output_path, world=world)

        if args.sync:
            sim_world.tick()
        else:
            sim_world.wait_for_tick()

        collector.start()

        clock = pygame.time.Clock()
        while True:
            clock.tick_busy_loop(args.sample_rate)
            if args.sync:
                sim_world.tick()
            if controller.parse_events(client, world, clock, args.sync):
                return
            world.tick(clock)
            snapshot = world.get_simulation_snapshot()
            timestamp = snapshot.timestamp.elapsed_seconds
            frame = snapshot.frame
            collector.record(timestamp, frame)
            world.render(display)
            pygame.display.flip()

    finally:
        collector.stop()

        if original_settings:
            sim_world.apply_settings(original_settings)

        if world and world.recording_enabled:
            client.stop_recorder()

        if world is not None:
            world.destroy()

        pygame.quit()


def generate_dataset(args: argparse.Namespace):
    """
    Handle generate dataset mode.

    Parameters
    ----------
    args : argparse.Namespace
        Input arguments.

    """
    config_path = args.cfg
    input_path = args.input

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    if "dataset" not in config:
        raise ValueError("Missing dataset entry.")

    dataset_cfg = config["dataset"]
    dataset_type = get_dataset_from_name(dataset_cfg["type"])

    attributes = dataset_cfg["attributes"]
    dataset = dataset_type(input_path, **attributes)

    dataset.generate_dataset()
    logging.info(
        f"Dataset generated and saved at: {dataset.get_output_path()}"
    )


def manual(args: argparse.Namespace):
    """
    Handle manual mode.

    Parameters
    ----------
    args : argparse.Namespace
        Input arguments.

    """
    supported_objects = get_list_of_docs_objects()

    object_name = args.object_name

    if object_name not in supported_objects:
        logging.error(f"Unknow class: {object_name}")
        return

    obj_class = get_object_from_name(object_name)

    logging.info(f"{object_name}: {obj_class.__doc__}")


def manual_parser(args: List[str]) -> argparse.Namespace:
    """
    Parse manual releated
    arguments.

    Parameters
    ----------
    args : List[str]
        Arguments to parse.

    Returns
    -------
    argparse.Namespace
        Namespace with parsed arguments.

    """
    argparser = argparse.ArgumentParser(
        description="CARLA Manual Control Client Manual"
    )

    argparser.add_argument(
        "object_name",
        choices=get_list_of_docs_objects(),
        help="Name of the object to show info about.",
    )

    return argparser.parse_args(args)


def game_parser(args: List[str]) -> argparse.Namespace:
    """
    Parse simulation releated
    arguments.

    Parameters
    ----------
    args : List[str]
        Arguments to parse.

    Returns
    -------
    argparse.Namespace
        Namespace with parsed arguments.

    """
    argparser = argparse.ArgumentParser(
        description="CARLA Manual Control Client Simulation"
    )

    argparser.add_argument(
        "--host",
        metavar="H",
        default="127.0.0.1",
        help="IP of the host server (default: 127.0.0.1)",
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="P",
        default=2000,
        type=int,
        help="TCP port to listen to (default: 2000)",
    )
    argparser.add_argument(
        "-a", "--autopilot", action="store_true", help="enable autopilot"
    )
    argparser.add_argument(
        "--res",
        metavar="WIDTHxHEIGHT",
        default="1280x720",
        help="window resolution (default: 1280x720)",
    )
    argparser.add_argument(
        "--filter",
        metavar="PATTERN",
        default="vehicle.*",
        help='actor filter (default: "vehicle.*")',
    )
    argparser.add_argument(
        "--generation",
        metavar="G",
        default="2",
        help="restrict to certain actor "
        "generation (values: '1','2','All' - default: '2')",
    )
    argparser.add_argument(
        "--rolename",
        metavar="NAME",
        default="hero",
        help='actor role name (default: "hero")',
    )
    argparser.add_argument(
        "--sample_rate",
        default=100.0,
        type=float,
        help="Sample rate in which data will be collected.",
    )
    argparser.add_argument(
        "--gamma",
        default=2.2,
        type=float,
        help="Gamma correction of the camera (default: 2.2)",
    )
    argparser.add_argument(
        "--sync",
        action="store_true",
        help="Activate synchronous mode execution",
    )
    argparser.add_argument(
        "--output",
        metavar="o",
        default="sample.csv",
        help="Path to output file where data will be stored",
    )
    argparser.add_argument(
        "--cfg",
        metavar="c",
        default=None,
        required=True,
        help="Path to the config file with sensors definition",
    )

    return argparser.parse_args(args)


def dataset_parser(args: List[str]) -> argparse.Namespace:
    """
    Parse dataset generation releated
    arguments.

    Parameters
    ----------
    args : List[str]
        Arguments to parse.

    Returns
    -------
    argparse.Namespace
        Namespace with parsed arguments.

    """
    argparser = argparse.ArgumentParser(
        description="CARLA Manual Control Client Dataset generator"
    )

    argparser.add_argument(
        "--input",
        metavar="o",
        default="sample.csv",
        help="Path to file with readings",
    )
    argparser.add_argument(
        "--cfg",
        metavar="c",
        default=None,
        required=True,
        help="Path to the config file with sensors definition",
    )

    return argparser.parse_args(args)


def parse_app_args() -> Tuple[argparse.Namespace, List[str]]:
    """
    Parse program command line arguments.

    Returns
    -------
    Tuple[argparse.Namespace,List[str]]
        Tuple with parsed namespace and
        unparsed arguments.

    """
    argparser = argparse.ArgumentParser(
        description="CARLA Manual Control Client", add_help=False
    )

    argparser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="debug",
        help="print debug information",
    )
    argparser.add_argument(
        "mode",
        default="sim",
        choices=["sim", "dataset", "man"],
        help="Select between collecting data in simulation, "
        "dataset generation or manual description.",
    )
    return argparser.parse_known_args()


def main():
    """
    Main program function.
    """

    args, unparsed = parse_app_args()

    mode = args.mode

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    try:
        if mode == "sim":
            args = game_parser(unparsed)
            logging.info(f"listening to server {args.host}:{args.port}")
            game_loop(args)
        elif mode == "dataset":
            args = dataset_parser(unparsed)
            generate_dataset(args)
        elif mode == "man":
            args = manual_parser(unparsed)
            manual(args)

    except KeyboardInterrupt:
        logging.info("\nCancelled by user. Bye!")


if __name__ == "__main__":
    main()
