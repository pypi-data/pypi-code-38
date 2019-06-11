import unittest

from grasping_type_inference.test \
    import get_test_true_mln_database, get_test_ground_atoms, get_test_false_mln_database


class AllGroundAtomsWithTheirTruthValuesTest(unittest.TestCase):
    def test_should_return_all_true_ground_atoms(self):
        self.__test__ground_atoms__(get_test_true_mln_database(), 1.0)

    def test_should_return_all_false_ground_atoms(self):
        self.__test__ground_atoms__(get_test_false_mln_database(), 0.0)

    def __test__ground_atoms__(self, test_database, expected_truth_value):
        ground_atoms_with_their_truth_values = test_database.get_ground_atoms_with_truth_values()
        self.__test_returned_ground_atoms__(ground_atoms_with_their_truth_values, expected_truth_value)

    def __test_returned_ground_atoms__(self, ground_atoms_with_their_truth_values,  expected_truth_value):
        test_true_ground_atoms = set(get_test_ground_atoms())
        is_ran_through_loop = False

        for ground_atom, truth_value in ground_atoms_with_their_truth_values:
            is_ran_through_loop = True
            self.assertEqual(truth_value, expected_truth_value)
            self.assertEqual(ground_atom in test_true_ground_atoms, True)

        self.assertEqual(is_ran_through_loop, True)


if __name__ == '__main__':
    unittest.main()
