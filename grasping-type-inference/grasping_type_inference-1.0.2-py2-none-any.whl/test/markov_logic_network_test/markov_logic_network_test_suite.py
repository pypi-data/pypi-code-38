from ground_atom_builder_test.ground_atom_builder_test_suite import GroundAtomBuilderSuite
from database_test.database_test_suite import DatabaseTestSuite
import unittest

test_suites = [
    GroundAtomBuilderSuite(),
    DatabaseTestSuite()
]

if __name__ == "__main__":
    main_suite = unittest.TestSuite(test_suites)
    runner = unittest.TextTestRunner()
    result = runner.run(main_suite)