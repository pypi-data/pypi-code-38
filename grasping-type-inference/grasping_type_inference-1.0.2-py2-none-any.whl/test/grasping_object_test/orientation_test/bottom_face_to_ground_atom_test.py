import unittest
from grasping_type_inference.face import Face
from grasping_type_inference.grasping_object import Orientation


class BottomFaceToGroundAtomTest(unittest.TestCase):
    def test_should_return_bottom_face_left_as_ground_atom(self):
        expected_value = "bottom_face(left)"
        orientation = Orientation(Face.TOP, Face.LEFT)

        self.assertEqual(orientation.transform_bottom_face_to_ground_atom(), expected_value)


if __name__ == "__main__":
    unittest.main()