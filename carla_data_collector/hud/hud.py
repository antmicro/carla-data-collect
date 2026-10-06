# Copyright (c) 2026 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides implementations for Head up displays.
"""

import datetime
import math
import os
from typing import TYPE_CHECKING, Tuple

import carla
import pygame

from carla_data_collector.sensors.gnss import GnssSensor
from carla_data_collector.sensors.imu import IMUSensor
from carla_data_collector.utils import get_actor_display_name

if TYPE_CHECKING:
    from carla_data_collector.world.world import World


class FadingText:
    """
    A text used to display temporary information on screen.
    """

    def __init__(
        self,
        font: pygame.font.Font,
        dim: Tuple[int, int],
        pos: Tuple[float, float],
    ):
        """
        Fading text initialization.

        Parameters
        ----------
        font : pygame.font.Font
            Font used by text.
        dim : Tuple[int,int]
            Text dimensions.
        pos : Tuple[float,float]
            Position of the text.

        """
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(
        self,
        text: str,
        color: Tuple[int, int, int] = (255, 255, 255),
        seconds: float = 2.0,
    ):
        """
        Set text to display.

        Parameters
        ----------
        text : str
            Text to display.
        color : Tuple[int,int,int]
            Text's color.
        seconds : float
            Number of seconds to keep
            text visible.

        """
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, clock: pygame.time.Clock):
        """
        Update loop.

        Parameters
        ----------
        clock : pygame.time.Clock
            Clock used for time
            measurments.

        """
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display: pygame.Surface):
        """
        Render text.

        Parameters
        ----------
        display : pygame.Surface
            Image to draw text into.

        """
        display.blit(self.surface, self.pos)


class HelpText:
    """
    Helper class to handle text output using pygame.
    """

    def __init__(
        self, font: pygame.font.Font, width: int, height: int, hel_str: str
    ):
        """
        Initialize help text.

        Parameters
        ----------
        font : pygame.font.Font
            Font used by text.
        width : int
            Text's width.
        height : int
            Text's height.
        hel_str : str
            Text to display.

        """
        lines = hel_str.split("\n")
        self.font = font
        self.line_space = 18
        self.dim = (780, len(lines) * self.line_space + 12)
        self.pos = (
            0.5 * width - 0.5 * self.dim[0],
            0.5 * height - 0.5 * self.dim[1],
        )
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * self.line_space))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        """Show/hide text."""
        self._render = not self._render

    def render(self, display: pygame.Surface):
        """
        Render text.

        Parameters
        ----------
        display : pygame.Surface
            Image to draw text into.

        """
        if self._render:
            display.blit(self.surface, self.pos)


class HUD:
    """
    HUD for displaying basic information on screen.
    """

    def __init__(self, width: int, height: int, help_str: str):
        """
        Initialize Head up display.

        Parameters
        ----------
        width : int
            Width of the HUD.
        height : int
            Height of the HUD.
        help_str : str
            String with help message.

        """
        self.dim = (width, height, help_str)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        font_name = "courier" if os.name == "nt" else "mono"
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = "ubuntumono"
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 12 if os.name == "nt" else 14)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        self.help = HelpText(
            pygame.font.Font(mono, 16), width, height, help_str
        )
        self.server_fps = 0
        self.frame = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

        self._show_ackermann_info = False
        self._ackermann_control = carla.VehicleAckermannControl()

    def on_world_tick(self, timestamp: carla.Timestamp):
        """
        Function called on world's update
        loop call.

        Parameters
        ----------
        timestamp : carla.Timestamp
            Information about elapsed simulation
            timestamp.

        """
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world: "World", clock: pygame.time.Clock):
        """
        HUD update function.

        Parameters
        ----------
        world : World
            Simulation world.
        clock : pygame.time.Clock
            Clock used to get elapsed time.

        """
        self._notifications.tick(clock)
        if not self._show_info:
            return
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        vehicles = world.world.get_actors().filter("vehicle.*")
        self._info_text = [
            f"Server: {self.server_fps:.0f} FPS",
            f"Client: {clock.get_fps():.0f} FPS",
            "",
            f"Vehicle: {get_actor_display_name(world.player, truncate=20)}",
            f"Map:     {
                datetime.timedelta(seconds=int(self.simulation_time))
            }",
            f"Simulation time: {
                datetime.timedelta(seconds=int(self.simulation_time))
            }",
            "",
            f"Speed:   {3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2):.2f} km/h",
            "",
            f"Location: ({t.location.x:.2f},{t.location.y:.2f})",
            f"Height: {t.location.z:.3f} m",
            "",
            f"Number of vehicles: {len(vehicles)}",
            "",
        ]

        for sensor in world.sensors:
            if isinstance(sensor, IMUSensor):
                compass = sensor.compass
                heading = "N" if compass > 270.5 or compass < 89.5 else ""
                heading += "S" if 90.5 < compass < 269.5 else ""
                heading += "E" if 0.5 < compass < 179.5 else ""
                heading += "W" if 180.5 < compass < 359.5 else ""
                self._info_text.extend([
                    f"Name: {sensor.name}",
                    f"Compass: {compass:.2f}\N{DEGREE SIGN} {heading}",
                    f"Accelero: ({sensor.accelerometer[0]:.3f},"
                    f"{sensor.accelerometer[1]:.3f},"
                    f"{sensor.accelerometer[2]:.3f})",
                    f"Gyroscop: ({sensor.gyroscope[0]:.3f},"
                    f"{sensor.gyroscope[1]:.3f},"
                    f"{sensor.gyroscope[2]:.3f})",
                    "",
                ])
            elif isinstance(sensor, GnssSensor):
                self._info_text.extend([
                    f"Name: {sensor.name}",
                    f"GNSS: {sensor.lat:.6f} {sensor.lon:.6f}",
                    "",
                ])

        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ("Throttle:", c.throttle, 0.0, 1.0),
                ("Steer:", c.steer, -1.0, 1.0),
                ("Brake:", c.brake, 0.0, 1.0),
                ("Reverse:", c.reverse),
                ("Hand brake:", c.hand_brake),
                ("Manual:", c.manual_gear_shift),
                f"Gear:        { {-1: 'R', 0: 'N'}.get(c.gear, c.gear) }",
            ]
            if self._show_ackermann_info:
                self._info_text += [
                    "",
                    "Ackermann Controller:",
                    "  Target speed:"
                    f" {3.6 * self._ackermann_control.speed:.2f} km/h",
                ]
        elif isinstance(c, carla.WalkerControl):
            self._info_text += [
                ("Speed:", c.speed, 0.0, 5.556),
                ("Jump:", c.jump),
            ]
        if len(vehicles) > 1:
            self._info_text += ["Nearby vehicles:"]

            def distance(dist):
                return math.sqrt(
                    (dist.x - t.location.x) ** 2
                    + (dist.y - t.location.y) ** 2
                    + (dist.z - t.location.z) ** 2
                )

            vehicles = [
                (distance(x.get_location()), x)
                for x in vehicles
                if x.id != world.player.id
            ]
            for d, vehicle in sorted(
                vehicles, key=lambda vehicles: vehicles[0]
            ):
                if d > 200.0:
                    break
                vehicle_type = get_actor_display_name(vehicle, truncate=22)
                self._info_text.append(f"{d:0.2f}m {vehicle_type}")

    def show_ackermann_info(self, enabled: bool):
        """
        Enable or disable ackermann information.

        Parameters
        ----------
        enabled : bool
            When set to true enables ackermann
            info, otherwise disable it.

        """
        self._show_ackermann_info = enabled

    def update_ackermann_control(
        self, ackermann_control: carla.VehicleAckermannControl
    ):
        """
        Set Ackermann Controller.

        Parameters
        ----------
        ackermann_control : carla.VehicleAckermannControl
            Ackerman controller to be used by simulation.

        """
        self._ackermann_control = ackermann_control

    def toggle_info(self):
        """Enable/disable on-screen information."""
        self._show_info = not self._show_info

    def notification(self, text: str, seconds: float = 2.0):
        """
        Show notification for specified amount of seconds.

        Parameters
        ----------
        text : str
            Text to display.
        seconds : float
            Amount of seconds text will be visible.

        """
        self._notifications.set_text(text, seconds=seconds)

    def error(self, text: str):
        """
        Show error message.

        Parameters
        ----------
        text : str
            Error message to display.

        """
        self._notifications.set_text(f"Error: {text}", (255, 0, 0))

    def render(self, display: pygame.Surface):
        """
        Render HUD to selected image.

        Parameters
        ----------
        display : pygame.Surface
            Image into which HUD will be
            rendered.

        """
        if self._show_info:
            info_surface = pygame.Surface((220, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break
                if isinstance(item, list):
                    if len(item) > 1:
                        points = [
                            (x + 8, v_offset + 8 + (1.0 - y) * 30)
                            for x, y in enumerate(item)
                        ]
                        pygame.draw.lines(
                            display, (255, 136, 0), False, points, 2
                        )
                    item = None
                    v_offset += 18
                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect(
                            (bar_h_offset, v_offset + 8), (6, 6)
                        )
                        pygame.draw.rect(
                            display, (255, 255, 255), rect, 0 if item[1] else 1
                        )
                    else:
                        rect_border = pygame.Rect(
                            (bar_h_offset, v_offset + 8), (bar_width, 6)
                        )
                        pygame.draw.rect(
                            display, (255, 255, 255), rect_border, 1
                        )
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect(
                                (
                                    bar_h_offset + f * (bar_width - 6),
                                    v_offset + 8,
                                ),
                                (6, 6),
                            )
                        else:
                            rect = pygame.Rect(
                                (bar_h_offset, v_offset + 8),
                                (f * bar_width, 6),
                            )
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]
                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(
                        item, True, (255, 255, 255)
                    )
                    display.blit(surface, (8, v_offset))
                v_offset += 18
        self._notifications.render(display)
        self.help.render(display)
