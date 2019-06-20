import unittest
from openProduction.suite import TestClass, TestLoader

class TCCorrect(TestClass.TestClass):
    """doc class"""

    def __init__(self):
        pass

    def step__00100(self):
        """Step 1 example"""
        pass

    def step__00200(self):
        """Step 2 example"""
        pass

class TCNoBase:
    """doc class"""

    def __init__(self):
        pass

    def step__00100(self):
        """Step 1 example"""
        pass



class TestSuiteTests(unittest.TestCase):

    def test_correct_class(self):
        """Test if loading a correct inherited class works"""
        tc = TCCorrect()
        a = TestLoader.TestLoaderClass(tc)
        ts = a.discover()
        self.assertEqual(len(ts.getTestCases()), 2)
        
    def test_no_base_class(self):
        """Test if loading a test class without TestClass as base fails"""
        tc = TCNoBase()
        self.assertRaises(RuntimeError, TestLoader.TestLoaderClass, tc)
        
if __name__ == '__main__':
    unittest.main()