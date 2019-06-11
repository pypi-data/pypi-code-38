import unittest
import markov_logic_network.ground_atom_builder as gab
from grasping_type_inference.test import FACING_ROBOT_FACE, BOTTOM_FACE, GRASPING_OBJECT_TYPE, GRASP_TYPE


class GroundAtomBuilderTest(unittest.TestCase):
    def test_should_return_a_valid_facing_robot_face_ground_atom(self):
        facing_robot_face_ground_atom = gab.get_facing_robot_face(FACING_ROBOT_FACE)
        expected_ground_atom = 'facing_robot_face(front)'

        self.assertEqual(facing_robot_face_ground_atom, expected_ground_atom)

    def test_should_return_a_valid_bottom_face_ground_atom(self):
        bottom_face_ground_atom = gab.get_bottom_face(BOTTOM_FACE)
        expected_ground_atom = 'bottom_face(bottom)'

        self.assertEqual(bottom_face_ground_atom, expected_ground_atom)

    def test_should_return_a_valid_obj_to_be_grasped_ground_atom(self):
        obj_to_be_grasped_ground_atom = gab.get_obj_to_be_grasped(GRASPING_OBJECT_TYPE)
        expected_ground_atom = 'obj_to_be_grasped({})'.format(GRASPING_OBJECT_TYPE)

        self.assertEqual(obj_to_be_grasped_ground_atom, expected_ground_atom)

    def test_should_return_a_valid_is_rotationally_symmetric_ground_atom(self):
        is_rotationally_symmetric_ground_atom = gab.get_is_rotationally_symmetric(GRASPING_OBJECT_TYPE)
        expected_ground_atom = 'is_rotationally_symmetric({})'.format(GRASPING_OBJECT_TYPE)

        self.assertEqual(is_rotationally_symmetric_ground_atom, expected_ground_atom)

    def test_should_return_a_valid_grasp_type_ground_atom(self):
        grasp_type_ground_atom = gab.get_grasp_type(GRASP_TYPE)
        expected_ground_atom = 'grasp_type({})'.format(GRASP_TYPE)

        self.assertEqual(grasp_type_ground_atom, expected_ground_atom)


if __name__ == "__main__":
    unittest.main()