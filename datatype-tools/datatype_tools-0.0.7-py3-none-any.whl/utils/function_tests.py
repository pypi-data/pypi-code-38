import unittest
import doctest
from utils import dict_functions
from utils import list_functions
from utils import string_functions
from utils import float_functions

testSuite = unittest.TestSuite()
for mod in dict_functions, list_functions, string_functions, float_functions:
	testSuite.addTest(doctest.DocTestSuite(mod))
unittest.TextTestRunner().run(testSuite)
