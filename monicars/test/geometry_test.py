#!/usr/bin/env python
import unittest
from util import Rectangle


class RectangleTest(unittest.TestCase):

    def test_pt_inside(self):
        rect = Rectangle([[100, 100], [200, 100], [200, 300], [100, 300]])
        in_pt = (150, 200)
        out_pt1 = (100, 100)
        out_pt2 = (400, 300)
        out_pt3 = (50, 50)
        out_pt4 = (150, 50)

        self.assertTrue(rect.is_inside(in_pt))
        self.assertFalse(rect.is_inside(out_pt1))
        self.assertFalse(rect.is_inside(out_pt2))
        self.assertFalse(rect.is_inside(out_pt3))
        self.assertFalse(rect.is_inside(out_pt4))

    def test_rect_intersect(self):
        rect = Rectangle([[100, 100], [200, 100], [200, 300], [100, 300]])
        rect1 = Rectangle([[150, 140], [250, 140], [250, 350], [150, 350]])
        rect2 = Rectangle([[400, 400], [500, 400], [500, 600], [400, 600]])

        self.assertTrue(rect.overlaps(rect1))
        self.assertFalse(rect.overlaps(rect2))


if __name__ == '__main__':
    unittest.main()
