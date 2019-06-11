import unittest
"""
This code will gather and run all the tests in this directory. Files with tests must start with the "test_" prefix.
"""

loader = unittest.TestLoader()
testSuite = loader.discover(".")

testRunner = unittest.TextTestRunner(verbosity=2)
testRunner.run(testSuite)
