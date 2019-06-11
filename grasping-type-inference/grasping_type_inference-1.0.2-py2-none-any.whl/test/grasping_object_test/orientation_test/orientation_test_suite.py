from bottom_face_to_ground_atom_test import BottomFaceToGroundAtomTest
from eq_test import EqualsTest
from facing_robot_face_to_ground_atom_test import FacingRobotFaceToGroundAtomTest
import unittest

test_cases = [
    BottomFaceToGroundAtomTest,
    EqualsTest,
    FacingRobotFaceToGroundAtomTest
]


class OrientationTestSuite(unittest.TestSuite):
    def __init__(self):
        test_suits = [unittest.makeSuite(x) for x in test_cases]
        unittest.TestSuite.__init__(self, test_suits)


if __name__ == "__main__":
    unittest.main()

