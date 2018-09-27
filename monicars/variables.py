#!/usr/bin/env python
"""Class for loading and accessing variables."""
from __future__ import print_function

import os
import yaml


ABS_PATH = os.path.dirname(os.path.realpath(__file__))


class _AgentVariables(object):
    """Variables belonging to agent initialization.

    Args:
        USE_POS: Whether to use this pose or the one defined in the map yaml.
        X: The initial X position.
        Y: The initial Y position.
        THETA: The initial angle.
        SPEED: The initial speed.
        NOISE: Whether to add noise to the initial conditions.
        STD_X: The standard deviation of noise on X.
        STD_Y: The standard deviation of noise on Y.
        STD_THETA: The standard deviation of noise on theta.
        STD_SPEED: The standard deviation of noise on speed.
    """
    def __init__(self, variables=None):
        if variables is not None:
            self.USE_POS = variables["use_pos"]
            self.X = variables["x"]
            self.Y = variables["y"]
            self.THETA = variables["theta"]
            self.SPEED = variables["speed"]
            self.NOISE = variables["add_noise"]
            self.STD_X = variables["std_x"]
            self.STD_Y = variables["std_y"]
            self.STD_THETA = variables["std_theta"]
            self.STD_SPEED = variables["std_speed"]

    def set(self, variables):
        self.USE_POS = variables["use_pos"]
        self.X = variables["x"]
        self.Y = variables["y"]
        self.THETA = variables["theta"]
        self.SPEED = variables["speed"]
        self.NOISE = variables["add_noise"]
        self.STD_X = variables["std_x"]
        self.STD_Y = variables["std_y"]
        self.STD_THETA = variables["std_theta"]
        self.STD_SPEED = variables["std_speed"]


class _ScreenVariables(object):
    """Variables belonging to agent initialization.

    Args:
        HEIGHT: The height of the screen.
        WIDTH: The width of the screen.
    """
    def __init__(self, variables=None):
        if variables is not None:
            self.HEIGHT = variables["height"]
            self.WIDTH = variables["width"]

    def set(self, variables):
        self.HEIGHT = variables["height"]
        self.WIDTH = variables["width"]


class _GlobalVariables(object):
    """Global variables.

    Attributes:
        FPS: The frames per second of the simulator.
        MAX_ANGLE: The maximum possible steering angle.
        MAX_ACC: The maximum possible acceleration.
        MAX_SPEED: The maximum possible speed.
        PATH: The path to the monicars directory.
        ENV: The environment name. Needs to be set after initialization.
    """
    def __init__(self, variables=None):
        if variables is not None:
            self.FPS = variables["fps"]
            self.MAX_ANGLE = variables["max_angle"]
            self.MAX_ACC = variables["max_acc"]
            self.MAX_SPEED = variables["max_speed"]

        self.PATH = os.path.dirname(os.path.realpath(__file__))
        self.ENV = "none"

    def set(self, variables):
        self.FPS = variables["fps"]
        self.MAX_ANGLE = variables["max_angle"]
        self.MAX_ACC = variables["max_acc"]
        self.MAX_SPEED = variables["max_speed"]


class _TrafficVariables(object):
    """Traffic variables.

    Attributes:
        FREQ: The probability of a new car appearing per second.
        MAX_CARS: The maximum number of cars, not including the obstacle.
        SPEED: The speed of the NPC cars.
        TYPES: The types of car available.
    """
    def __init__(self, variables=None):
        if variables is not None:
            self.FREQ = variables["freq"] / global_var.FPS
            self.MAX_CARS = variables["max_cars"]
            self.SPEED = variables["speed"]

        self.TYPES = ["blue_car", "green_car", "pink_car",
                      "teal_car", "white_car", "yellow_car"]

    def set(self, variables):
        self.FREQ = variables["freq"] / global_var.FPS
        self.MAX_CARS = variables["max_cars"]
        self.SPEED = variables["speed"]


class _ObstacleVariables(object):
    """Variables belonging to obstacke NPC.

    Attributes:
        X: Initial X position (int, pixels).
        Y: Initial Y position (int, pixels).
        THETA: Initial angle (float, radians).
        SPEED: Initial speed (float, pixels/sec).
        CRASH: Whether the obstacle car should crash with some probability (bool).
        PROB_CRASH: The probability that the obstacle crashes in the episode (float).
        CRASH_Y: The Y position at which the obstacle will crash (pixels).
        NOISE: Whether to add noise to the initial state (bool).
        STD_X: The standard deviation of the X position.
        STD_Y: The standard deviation of the Y position.
        STD_SPEED: The standard deviation of the speed.
    """
    def __init__(self, variables=None):
        if variables is not None:
            self.X = variables["x"]
            self.Y = variables["y"]
            self.THETA = variables["theta"]
            self.SPEED = variables["speed"]
            self.CRASH = variables["crash"]
            self.PROB_CRASH = variables["prob_crash"]
            self.CRASH_Y = variables["crash_y"]
            self.NOISE = variables["noise"]
            self.STD_X = variables["std_x"]
            self.STD_Y = variables["std_y"]
            self.STD_SPEED = variables["std_speed"]
            self.TOTAL_STUCK_TIME = variables["total_stuck_time"]

    def set(self, variables):
        self.X = variables["x"]
        self.Y = variables["y"]
        self.THETA = variables["theta"]
        self.SPEED = variables["speed"]
        self.CRASH = variables["crash"]
        self.PROB_CRASH = variables["prob_crash"]
        self.CRASH_Y = variables["crash_y"]
        self.NOISE = variables["noise"]
        self.STD_X = variables["std_x"]
        self.STD_Y = variables["std_y"]
        self.STD_SPEED = variables["std_speed"]
        self.TOTAL_STUCK_TIME = variables["total_stuck_time"]



global_var = _GlobalVariables()
agent = _AgentVariables()
screen = _ScreenVariables()
traffic = _TrafficVariables()
obstacle = _ObstacleVariables()


def load_variables(file_path):
    """Loads the variables and save them to default variables.

    Args:
        file_path: Path to the config file.
    """
    with open(file_path) as f:
        var = yaml.load(f)

    # These variables can be accessed from other files.
    global_var.set(var["global"])
    agent.set(var["init"])
    screen.set(var["visualization"])
    traffic.set(var["traffic"])
    obstacle.set(var["obstacle"])


def set_env(name):
    """Set the environment name."""
    if global_var is not None:
        global_var.ENV = name


# Default config file.
load_variables(os.path.join(ABS_PATH, "config/config.yaml"))
