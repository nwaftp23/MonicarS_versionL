"""Agent description."""
import os
import pygame
from variables import agent, global_var
from models import Unicycle
from util import Rectangle, add_noise


class Agent(Unicycle):
    """Our agent is a red car unicycle model."""

    def __init__(self, x=agent.X, y=agent.Y, theta=agent.THETA,
                 speed=agent.SPEED, name="red_car"):
        """Initializes the agent function.

        Args:
            x: Initial agent x position (pixels). Optional.
            y: Initial agent y position (pixels). Optional.
            theta: Initial agent angle (radians). Optional.
            speed: Initial agent speed (pixels/second). Optional.
            name: Name of the car image. Optional.
        """
        self.init_x = x
        self.init_y = y
        self.init_theta = theta
        self.init_speed = speed

        if agent.NOISE:
            x = add_noise(x, agent.STD_X)
            y = add_noise(y, agent.STD_Y)
            theta = add_noise(theta, agent.STD_THETA)
            speed = add_noise(speed, agent.STD_SPEED)

        super(Agent, self).__init__(x, y, theta, speed)

        self.name = name

        self.img = pygame.image.load(os.path.join(global_var.PATH, "media", name + ".png"))
        self.width = self.img.get_width()
        self.height = self.img.get_height()

        # Setup a simple bounding box of the correct size.
        self.bounding_box = Rectangle([[0, 0], [0, self.width], [self.height, self.width], [self.height, 0]])

        # Shift the bounding box to the correct orientation and position.
        self.bounding_box.move_to(x, y, theta)

    def reset(self, noise=True):
        """Resets the agent to the initial position.

        Args:
            noise: Whether to add noise when resetting. Defaults to True.
        """
        if agent.NOISE and noise:
            x = add_noise(self.init_x, agent.STD_X)
            y = add_noise(self.init_y, agent.STD_Y)
            theta = add_noise(self.init_theta, agent.STD_THETA)
            speed = add_noise(self.init_speed, agent.STD_SPEED)
        else:
            x = self.init_x
            y = self.init_y
            theta = self.init_theta
            speed = self.init_speed

        self.set_state(x, y, theta, speed)
        self.bounding_box.move_to(x, y, theta)

    def move(self, acc, heading):
        """Moves the agent forward one step.

        Args:
            acc: Acceleration command.
            heading: Steering command.
        """
        # Move the actual object.
        delta_x, delta_y, delta_theta = super(Agent, self).move(acc, heading)

        # Move its bounding box as well.
        self.bounding_box.transform(delta_x, delta_y, delta_theta)

    def in_map(self, width, height):
        """Returns True if the agent is inside a map of a given height and width
        and False otherwise."""
        x = self.get_x()
        y = self.get_y()
        return x <= width and y <= height and x >= 0 and y >= 0
