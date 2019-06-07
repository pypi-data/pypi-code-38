from get_all_ground_atoms_with_their_truth_values_test import AllGroundAtomsWithTheirTruthValuesTest
import unittest

test_cases = [AllGroundAtomsWithTheirTruthValuesTest]


class DatabaseTestSuite(unittest.TestSuite):
    def __init__(self):
        test_suits = [unittest.makeSuite(x) for x in test_cases]
        unittest.TestSuite.__init__(self, test_suits)


if __name__ == "__main__":
    unittest.main()
