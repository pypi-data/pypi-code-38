# Import unittest
import unittest

# Import core module main file for testing
from .perfectpypi_core import *

# Test case Class
class TestCoreModule(unittest.TestCase):
    
    currentResult = None # holds last result object passed to run method

    def setUp(self):
        pass

    # teardown for manage test case results
    def tearDown(self):
        ok = self.currentResult.wasSuccessful()
        errors = self.currentResult.errors
        failures = self.currentResult.failures
        print ('All tests passed so far!' if ok else \
                ' %d errors and %d failures so far' % \
                (len(errors), len(failures)))

    def run(self, result=None):
        self.currentResult = result # remember result for use in tearDown
        unittest.TestCase.run(self, result) # call superclass run method

    # Test Case 01 - Write out text in string format with default value
    def test_input(self):
        self.assertEqual(getText("test text"), "test text")

    # Test Case 02 - Write out text in string and json format
    def test_output(self):
        self.assertEqual(getText("test text", "string"), "test text")
        self.assertEqual(getText("test text", "json"), {"text": "test text"})

# Test runner function
def runUnittests():
    suite = unittest.TestSuite()
    # Check test cases in TestCoreModule class
    for method in dir(TestCoreModule):
        # Add test collection tests which start with "test"
        if method.startswith("test"):
            suite.addTest(TestCoreModule(method))
    # Return with execution and result of testcases
    return unittest.TextTestRunner(verbosity=3).run(suite)

# Run test if you use from __main__
#if __name__ == 'perfectpypi.core.perfectpypi_core_unittest':
    #unittest.main()
    
