#!/usr/bin/env python

import os
import sys
import pygame
import numpy as np
from variables import global_var

RED = (255, 0, 0)
BLUE = (0, 0, 255)


class View(object):

    """View handles the visualization part of the environment."""

    def __init__(self, env_name, env_width, env_height, screen_width=None, screen_height=None, flip=False):
        """Initializes View.

        Args:
            env_name: The name of the environment image to load.
            env_width: The width of the whole environment.
            env_height: The height of the whole environment.
            screen_width: The width of the screen to view. If None, whole env is displayed.
            screen_height: The height of the screen to view. If None, whole env is displayed.
            flip: Whether to flip the screen. For driving view.
        """
        self.flip = flip

        # Width of the whole environment.
        self.width = env_width
        self.height = env_height

        # Width of the view.
        self.screen_width = screen_width if screen_width is not None else env_width
        self.screen_height = screen_height if screen_height is not None else env_height

        # Whether the environment should follow the agent's view or show the whole env.
        self.scroll = self.width != self.screen_width or self.height != self.screen_height

        self.surface = None
        self.surface_flipped = None
        self.env_view = None

        self.trajectory = None  # The trajectory to draw onto the image.

        self.env_img = self._load_img(env_name)

        self.surface = pygame.Surface((self.screen_width, self.screen_height))
        self.surface_flipped = pygame.Surface((self.screen_width, self.screen_height))

    def update(self, x, y, characters):
        """Updates the view with all the characters.

        Args:
            x: The x coordinate around which to center the view.
            y: The y coordinate around which to center the view.
            characters: A list of tuples of form (img, x, y, theta) for each char.

        Returns:
            Surface object.
        """
        # Update the current view of the environment.
        self.env_view = self._get_current_view(x, y)

        # Draw a trajectory if it exists.
        if self.trajectory is not None:
            self._draw_trajectory()

        # Draw the environment onto the image.
        self.surface.blit(self.env_img, (0, 0), self.env_view)

        # Draw each character on the image.
        for img, x, y, theta in characters:
            self._draw_character(img, x, y, theta, self.env_view[0], self.env_view[1])

        # Flip the image if necessary.
        if self.flip:
            self.surface_flipped = pygame.transform.flip(self.surface, False, True)
            self.surface.blit(self.surface_flipped, (0, 0))

        return self.surface

    def draw_trajectory(self, trajectory):
        """Saves and draws trajectory which is a list of states. The states
        need to be of form (x, y). Call update to see the trajectory. TODO: Add
        theta and make arrows."""
        self.trajectory = trajectory
        self._draw_trajectory()

    def clear_trajectory(self):
        """Clears the trajectory from the view."""
        self.trajectory = None

    def _draw_trajectory(self):
        """Draws the actual trajectory onto the image."""
        if self.trajectory is None:
            return

        for state in self.trajectory:
            pygame.draw.circle(self.env_img, BLUE, (int(state[0]), int(state[1])), 2)

    def get_colour(self, x, y):
        """Returns the normalized RGB values of the pixel at x, y."""
        if x >= self.width or y >= self.height:
            return (0, 0, 0)

        return self.env_img.get_at((int(x), int(y))).normalize()[0:3]

    def _load_img(self, name):
        """Loads the image from the map directory."""
        try:
            img_path = os.path.join(global_var.PATH, "maps", name + ".png")
            env_img = pygame.image.load(img_path)
        except Exception as e:
            print(e)
            print("Environment", name, "does not exist. Make sure that a PNG image exists",
                  "under that name in the \"maps\" folder.")
            sys.exit()

        return env_img

    def _draw_character(self, img, x, y, theta, view_x=0, view_y=0):
        """Helper function to draw a character on the screen.

        Args:
            img: The image of the character object.
            x: The x position of the character.
            y: The y position of the character.
            theta: The character's heading.
            view_x: The x component of the corner of the current view.
            view_y: The y component of the corner of the current view.
        """
        # Rotate the image and get its dimensions.
        rotated = pygame.transform.rotate(img, np.degrees(theta))
        rect = rotated.get_rect()

        # Calculate the global position of the corner of the car within the map
        x_global = x - rect.width / 2.0
        y_global = y - rect.height / 2.0

        # The car should be displayed relative to the current view.
        x = x_global - view_x
        y = y_global - view_y

        self.surface.blit(rotated, (int(round(x)), int(round(y))))

    def _get_current_view(self, agent_x, agent_y):
        """Gets the coordinates of what the current view should be so that the
        view follows the agent."""
        # If scroll is False, the current view is always the whole image.
        if not self.scroll:
            return (0, 0, self.width, self.height)

        x = agent_x
        y = agent_y
        w = self.screen_width
        h = self.screen_height

        # This is the amount by which the current view selection overshoots the
        # actual size of the environment.
        overshoot_x = max(x + w / 2 - self.width, 0) % self.width
        overshoot_y = max(y + h / 2 - self.height, 0) % self.height

        # Make sure that the view will be inside the environment.
        corner_x = max(x - w / 2 - overshoot_x, 0)
        corner_y = max(y - h / 2 - overshoot_y, 0)

        return (int(round(corner_x)), int(round(corner_y)), w, h)


if __name__ == '__main__':
    # Test code for drawing trajectories and moving along them.
    from agent import Agent

    display_surface = pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
    pygame.display.set_caption('Traffic World')

    pygame.init()

    view = View("two_lanes", 500, 1500, 500, 500)
    agent = Agent()

    trajectory = [(300, 40),
                  (300, 45),
                  (300, 50),
                  (300, 55),
                  (300, 60),
                  (300, 65),
                  (300, 70),
                  (300, 75),
                  (300, 80),
                  (300, 85),
                  (300, 90),
                  (300, 95),
                  (300, 100),
                  (300, 105),
                  (300, 110),
                  (300, 115),
                  (300, 120),
                  (300, 125),
                  (300, 130)]

    view.draw_trajectory(trajectory)

    for state in trajectory:
        surf = view.update(state[0], state[1], [(agent.img, state[0], state[1], 0)])

        display_surface.blit(surf, (0, 0))
        pygame.display.update()
        clock.tick(15)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

    pygame.quit()
