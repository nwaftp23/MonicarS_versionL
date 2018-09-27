#!/usr/bin/env python
"""Code to control the car from the keyboard with AWD"""

import sys
import pygame
from monicars import Environment
from monicars import Agent

__author__ = "Jana Pavlasek"
__version__ = "0.1.0"


def to_cmd(event):
    """Translates keyboard command to BoolPose message.

    Args:
        event: Keyboard event.

    Returns:
        Action array.
    """
    action = [0, 0]

    if event.key == pygame.K_LEFT:
        action = [0, -1]
    elif event.key == pygame.K_RIGHT:
        action = [0, 1]
    elif event.key == pygame.K_UP:
        pass
    elif event.key == pygame.K_DOWN:
        pass

    return action


if __name__ == '__main__':
    print "Reading from the keyboard."
    print "Use arrow keys to control the car. Use ^C to quit."

    if len(sys.argv) > 1:
        course = sys.argv[1]
    else:
        course = "track"

    env = Environment(course, flip=True, tick=True)

    env.reset()

    done = False
    # Enter main loop.
    while not done:
        action = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.KEYDOWN:
                action = to_cmd(event)

        _, _, done = env.step(action)
