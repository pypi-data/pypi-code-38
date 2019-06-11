import unittest
from grasping_type_inference.test \
    import get_rotationally_symmetrical_grasping_object, get_grasping_object_as_true_mln_database, \
            GRASPING_OBJECT_TYPE, FACING_ROBOT_FACE, BOTTOM_FACE
from markov_logic_network.grasping_type_mln import grasping_type_mln
import markov_logic_network.ground_atom_builder as gab


class TransformToMLNDatabase(unittest.TestCase):
    def test_should_return_a_valid_mln_database(self):
        grasping_object = get_rotationally_symmetrical_grasping_object()
        grasping_object_database = grasping_object.transform_to_mln_database(grasping_type_mln)
        expected_database = __get_expected_mln_database__()
        actual = grasping_object_database == expected_database
        self.assertEqual(actual, True)


def __get_expected_mln_database__():
    ground_atoms = [gab.get_bottom_face(BOTTOM_FACE),
                    gab.get_facing_robot_face(FACING_ROBOT_FACE),
                    gab.get_obj_to_be_grasped(GRASPING_OBJECT_TYPE),
                    gab.get_is_rotationally_symmetric(GRASPING_OBJECT_TYPE)]

    return get_grasping_object_as_true_mln_database(grasping_type_mln, ground_atoms)


if __name__ == "__main__":
    unittest.main()
