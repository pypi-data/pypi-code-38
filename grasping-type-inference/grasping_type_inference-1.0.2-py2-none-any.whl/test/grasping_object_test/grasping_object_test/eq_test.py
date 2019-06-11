import unittest
from grasping_type_inference.grasping_object import GraspingObject
from grasping_type_inference.test import FACING_ROBOT_FACE, BOTTOM_FACE


class EqualsTest(unittest.TestCase):
    def test_should_return_true_if_grasping_objects_are_equal(self):
        grasping_object_1 = GraspingObject(FACING_ROBOT_FACE, BOTTOM_FACE)
        grasping_object_2 = GraspingObject(FACING_ROBOT_FACE, BOTTOM_FACE)
        actual = grasping_object_1 == grasping_object_2
        self.assertEqual(actual, True)

    def test_should_return_false_if_grasping_objects_are_not_equal(self):
        grasping_object_1 = GraspingObject(FACING_ROBOT_FACE, BOTTOM_FACE)
        grasping_object_2 = GraspingObject(BOTTOM_FACE, FACING_ROBOT_FACE)
        actual = grasping_object_1 == grasping_object_2
        self.assertEqual(actual, False)


if __name__ == "__main__":
    unittest.main()


