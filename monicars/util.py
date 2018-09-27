"""Utility functions"""
from __future__ import print_function

import math
import numpy as np
from scipy.spatial.distance import euclidean
from variables import global_var

SMALL = 0.001


def input_to_action(usr_in):
    """Changes the user input to a usable form.

    Args:
        usr_in: The user input, in a range from -1 to 1 for acceleration and heading.

    Returns:
        The acceleration and steering commands in real units.
    """
    acc = np.clip(usr_in[0], -global_var.MAX_ACC, global_var.MAX_ACC)
    theta = np.clip(usr_in[1], -global_var.MAX_ANGLE, global_var.MAX_ANGLE)
    return acc, theta


def limit(num, minimum, maximum):
    """Returns a number limited between two bounds."""
    num = min(maximum, num)
    num = max(minimum, num)

    return num


def is_close(x, y, tol=0.05):
    """Returns True if x is within tol of y, False otherwise."""
    return abs(x - y) <= tol


def add_noise(num, std):
    """Adds Gaussian noise to an integer and returns an integer."""
    if type(num) == int:
        return int(round(np.random.normal(num, std, 1)[0]))
    else:
        return np.random.normal(num, std, 1)[0]


def normalize_angle(angle):
    """Returns an angle, normalized."""
    return (angle + np.pi) % (2 * np.pi) - np.pi


def points_eq(pt1, pt2):
    """Returns True if two points are equal and False otherwise."""
    x_eq = abs(pt1[0] - pt2[0]) < SMALL
    y_eq = abs(pt1[1] - pt2[1]) < SMALL
    return x_eq and y_eq


def on_segment(seg, pt, on_line=False):
    """Checks if a point is on a line."""
    # Is the pt on the line?
    if not on_line:
        cross = cross_product(seg, (pt, seg[0]))
        if abs(cross) > SMALL:
            return False

    seg_length = euclidean(seg[0], seg[1])

    # If the intersection of the two lines is within the segment, the legth of the
    # segment will be larger than the distance between the intersection and the end points.
    return seg_length > euclidean(seg[0], pt) and seg_length > euclidean(seg[1], pt)


def cross_product(u, v):
    """Cross product of two line segments."""
    x1 = u[1][0] - u[0][0]
    y1 = u[1][1] - u[0][1]
    x2 = v[1][0] - v[0][0]
    y2 = v[1][1] - v[0][1]

    return x1 * y2 - x2 * y1


def intersect(seg1, seg2):
    """Checks whether two line segments intersect."""
    cross = cross_product(seg1, seg2)

    # If the lines are parallel or colinear, we'll just say they don't intersect.
    if abs(cross) < SMALL:
        return True

    # Find the intersection point of the two lines by using determinants.
    x1 = seg1[1][0] - seg1[0][0]
    y1 = seg1[1][1] - seg1[0][1]
    x2 = seg2[1][0] - seg2[0][0]
    y2 = seg2[1][1] - seg2[0][1]
    det1 = seg1[0][0] * seg1[1][1] - seg1[0][1] * seg1[1][0]
    det2 = seg2[0][0] * seg2[1][1] - seg2[0][1] * seg2[1][0]

    int_x = (det1 * x2 - x1 * det2) / -cross
    int_y = (det1 * y2 - y1 * det2) / -cross

    intersection = (int_x, int_y)

    return on_segment(seg1, intersection, True) and on_segment(seg2, intersection, True)


class Point(object):
    def __init__(self, pt):
        self.x = pt[0]
        self.y = pt[1]


class Line(object):
    """Line object. TODO: incorporate into Rectangle. The first point is the top one."""
    def __init__(self, points):
        if points[0][1] < points[1][1]:
            self.pt1 = Point(points[0])
            self.pt2 = Point(points[1])
        else:
            self.pt1 = Point(points[1])
            self.pt2 = Point(points[0])

        self.theta = self.angle()  # Angle from x axis to line.

    def dist_to_point(self, pt):
        if not type(pt) == Point:
            pt = Point(pt)

        y_diff = self.pt2.y - self.pt1.y
        x_diff = self.pt2.x - self.pt1.x
        a = abs(y_diff * pt.x - x_diff * pt.y + self.pt2.x * self.pt1.y - self.pt2.y * self.pt1.x)
        b = np.sqrt(np.square(y_diff) + np.square(x_diff))

        return a / b

    def angle(self):
        y = self.pt2.y - self.pt1.y
        x = self.pt2.x - self.pt1.x
        return np.arctan2(x, y)


class Rectangle(object):
    """Rectangle object."""
    def __init__(self, points):
        if not self.check_rect(points):
            print("This is not a valid rectangle")
            raise
        self.points = points
        self.update_lines()

        self.width = euclidean(self.points[0], self.points[1])
        self.height = euclidean(self.points[1], self.points[2])

    def check_rect(self, points):
        """Check if an array is a valid rectangle. It must have four sets of
        points with two elements each."""
        if len(points) != 4:
            return False

        for pt in points:
            if len(pt) != 2:
                return False

        return True

    def update_lines(self):
        self.lines = ((self.points[0], self.points[1]),
                      (self.points[1], self.points[2]),
                      (self.points[2], self.points[3]),
                      (self.points[3], self.points[0]))

    def get_centre(self):
        sum_x = 0
        sum_y = 0
        for pt in self.points:
            sum_x += pt[0]
            sum_y += pt[1]

        return (sum_x / 4.0, sum_y / 4.0)

    def get_angle(self):
        o = self.points[1][0] - self.points[2][0]
        a = self.points[2][1] - self.points[1][1]
        return np.arctan2(o, a)

    def transform(self, x, y, theta):
        """Transforms the rectangle by a given position and angle."""
        self.rotate(theta)
        self.shift(x, y)

    def move_to(self, x, y, theta):
        """Moves the rectangle to a given position."""
        curr_theta = self.get_angle()
        curr_pos = self.get_centre()

        self.transform(x - curr_pos[0], y - curr_pos[1], theta - curr_theta)

    def shift(self, x, y):
        """Shifts the rectangle from its current position."""
        for pt in self.points:
            pt[0] += x
            pt[1] += y

        self.update_lines()

    def rotate(self, theta):
        """Rotates the rectangle about its current position."""
        # First we need to shift the shape to the origin.
        centre = self.get_centre()
        self.shift(-centre[0], -centre[1])

        # Rotate all the points about the origin.
        new_pts = []
        for pt in self.points:
            x_new = pt[0] * math.cos(theta) - pt[1] * math.sin(theta)
            y_new = pt[0] * math.sin(theta) + pt[1] * math.cos(theta)
            new_pts.append([x_new, y_new])

        self.points = new_pts

        # Shift the points back to the original centre.
        self.shift(centre[0], centre[1])

        self.update_lines()

    def is_inside(self, pt):
        """Checks if a point is inside the rectangle using the ray casting
        algorithm. If a ray from a point outside the polygon to our point
        intersects the polygon an even number of times, then it's outside,
        otherwise it's  inside. The point we choose is (0, 0). A point on the
        perimeter of the rectangle is outside.

        Args:
            pt: Point in the form (x, y).
        """
        ray = ((0, 0), pt)
        intersections = 0

        # Check whether lines intersect the ray.
        for line in self.lines:
            if intersect(ray, line):
                intersections += 1

        # Check whether the ray happens to cross a corner of the rectangle. This
        # will not be registered as an intersection so has to be checked separately.
        for corner in self.points:
            if on_segment(ray, corner):
                intersections += 1

        return intersections % 2 == 1

    def overlaps(self, rect):
        """Determines if a rectangle overlaps with itself. If any point in the
        rectangle is inside our rectangle, then they overlap."""
        for pt in rect.points:
            if self.is_inside(pt):
                return True

        return False

    def draw(self):
        """For debugging only."""
        colours = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0))
        for line, colour in zip(self.lines, colours):
            pygame.draw.line(display_surface, colour, line[0], line[1], 3)


if __name__ == '__main__':
    # Test rectangle functions.
    import pygame
    import time

    pygame.init()
    display_surface = pygame.display.set_mode((700, 700))
    clock = pygame.time.Clock()
    pygame.display.set_caption('Traffic World')
    pygame.display.update()

    rect1 = Rectangle([[571.0, 15.0], [535.0, 15.0], [535.0, 59.0], [571.0, 59.0]])
    rect = Rectangle([[468.0, 428.0], [432.0, 428.0], [432.0, 472.0], [468.0, 472.0]])
    pt = (150, 200)

    display_surface.fill((255, 255, 255))
    rect.draw()
    rect1.draw()
    pygame.draw.circle(display_surface, (0, 0, 0), pt, 4)
    pygame.display.update()

    print("Inside?", rect.is_inside(pt))
    print("Overlap?", rect.overlaps(rect1))
    # rect.draw()
    # pygame.display.update()

    # time.sleep(2)

    # print("Shift")

    # rect.shift(100, 100)
    # # display_surface.fill((255, 255, 255))
    # rect.draw()
    # pygame.display.update()

    # time.sleep(2)

    # print("Rotate")

    # rect.rotate(-1)
    # # display_surface.fill((255, 255, 255))
    # rect.draw()
    # pygame.display.update()

    # time.sleep(2)
    # print("Transform")

    # rect.transform(100, 100, 1)
    # rect.draw()
    # pygame.display.update()

    crashed = False
    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True

        pygame.display.update()
        clock.tick(60)
