import unittest

def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(test_loader.discover('rockset.tests'))
    test_suite.addTest(test_loader.discover('rockset.sql.tests'))
    test_suite.addTest(test_loader.discover('rockset.rock.tests'))
    return test_suite
