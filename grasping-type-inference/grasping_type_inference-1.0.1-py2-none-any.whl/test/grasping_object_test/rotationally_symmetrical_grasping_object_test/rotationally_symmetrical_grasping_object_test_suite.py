from eq_test import EqualsTest
from transform_to_mln_database_test import TransformToMLNDatabase
import unittest

test_cases = [
    EqualsTest,
    TransformToMLNDatabase
]


class RotationallySymmetricalGraspingObjectSuite(unittest.TestSuite):
    def __init__(self):
        test_suits = [unittest.makeSuite(x) for x in test_cases]
        unittest.TestSuite.__init__(self, test_suits)


if __name__ == "__main__":
    unittest.main()
