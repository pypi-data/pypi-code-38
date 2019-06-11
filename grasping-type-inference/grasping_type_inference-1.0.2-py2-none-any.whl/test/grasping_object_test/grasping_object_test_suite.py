from grasping_object_test.grasping_object_test_suite import GraspingObjectTestSuite as Gots
from orientation_test.orientation_test_suite import OrientationTestSuite
from rotationally_symmetrical_grasping_object_test.rotationally_symmetrical_grasping_object_test_suite \
    import RotationallySymmetricalGraspingObjectSuite
import unittest

test_suites = [
    OrientationTestSuite(),
    Gots(),
    RotationallySymmetricalGraspingObjectSuite()
]

if __name__ == "__main__":
    main_suite = unittest.TestSuite(test_suites)
    runner = unittest.TextTestRunner()
    result = runner.run(main_suite)

