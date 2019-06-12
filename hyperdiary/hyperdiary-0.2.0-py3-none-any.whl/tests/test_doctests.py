import doctest
import unittest

import hyperdiary.simplepath
import hyperdiary.diary

suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite(hyperdiary.simplepath))
suite.addTest(doctest.DocTestSuite(hyperdiary.diary))

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)