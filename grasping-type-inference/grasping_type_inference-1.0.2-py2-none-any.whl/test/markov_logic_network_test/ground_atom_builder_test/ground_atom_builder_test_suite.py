from ground_atom_builder_test import GroundAtomBuilderTest
import unittest

test_cases = [GroundAtomBuilderTest]


class GroundAtomBuilderSuite(unittest.TestSuite):
    def __init__(self):
        test_suits = [unittest.makeSuite(x) for x in test_cases]
        unittest.TestSuite.__init__(self, test_suits)


if __name__ == "__main__":
    unittest.main()
