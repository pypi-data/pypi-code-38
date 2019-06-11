import unittest
from grasping_type_inference.grasping_object import Orientation
from grasping_type_inference.test import FACING_ROBOT_FACE, BOTTOM_FACE


class EqualsTest(unittest.TestCase):
    def test_should_return_true_if_orientations_are_equal(self):
        orientation_1 = Orientation(FACING_ROBOT_FACE, BOTTOM_FACE)
        orientation_2 = Orientation(FACING_ROBOT_FACE, BOTTOM_FACE)
        actual = orientation_1 == orientation_2
        self.assertEqual(actual, True)

    def test_should_return_false_if_orientations_are_not_equal(self):
        orientation_1 = Orientation(FACING_ROBOT_FACE, BOTTOM_FACE)
        orientation_2 = Orientation(BOTTOM_FACE, FACING_ROBOT_FACE)
        actual = orientation_1 == orientation_2
        self.assertEqual(actual, False)


if __name__ == "__main__":
    unittest.main()


