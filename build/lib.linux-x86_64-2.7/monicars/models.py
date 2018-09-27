"""Models for motion."""
import math
from util import normalize_angle


class Unicycle(object):

    def __init__(self, x, y, theta, speed):
        """Initialize the unicycle object.

        Args:
            x: Initial x position (pixels).
            y: Initial y position (pixels).
            theta: Initial theta (radians).
            speed: Initial speed (pixels/timestep).
        """
        self._x = x  # pixels
        self._y = y  # pixels
        self._heading = theta  # radians
        self._speed = speed  # pixels/timestep

    def move(self, acc, heading):
        """Steps the object forward by one timestep using the unicycle model.

        Args:
            acc: Acceleration command.
            heading: Steering command.
        """
        # Since this is one timestep, we do not need to multiply by time.
        self._speed += acc
        
        steerAngle = self._speed * math.tan(heading) / 50.0
        self._heading += steerAngle
        
        self._heading = normalize_angle(self._heading)

        # Since this is one timestep, the speed is equal to the displacement.
        delta_x = self._speed * math.sin(self._heading)
        delta_y = self._speed * math.cos(self._heading)

        self._x += delta_x
        self._y += delta_y

        return (delta_x, delta_y, steerAngle)

    def get_state(self):
        """Returns the position of the object in format (x, y, theta)."""
        return (self._x, self._y, self._heading, self._speed)

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_pos(self):
        return (self._x, self._y)

    def get_heading(self):
        return self._heading

    def get_speed(self):
        return self._speed

    def set_state(self, x, y, theta, speed):
        self._speed = speed
        self._heading = theta
        self._x = x
        self._y = y

    def set_x(self, x):
        self.set_state(x, self._y, self._heading, self._speed)

    def set_y(self, y):
        self.set_state(self._x, y, self._heading, self._speed)

    def set_heading(self, theta):
        self.set_state(self._x, self._y, theta, self._speed)

    def set_speed(self, speed):
        self.set_state(self._x, self._y, self._heading, speed)
