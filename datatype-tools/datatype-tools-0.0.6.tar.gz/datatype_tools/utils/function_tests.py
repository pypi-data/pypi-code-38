import unittest
import doctest
from datatype_tools.utils import dict_functions
from datatype_tools.utils import list_functions
from datatype_tools.utils import string_functions
from datatype_tools.utils import float_functions

testSuite = unittest.TestSuite()
for mod in dict_functions, list_functions, string_functions, float_functions:
	testSuite.addTest(doctest.DocTestSuite(mod))
unittest.TextTestRunner().run(testSuite)
