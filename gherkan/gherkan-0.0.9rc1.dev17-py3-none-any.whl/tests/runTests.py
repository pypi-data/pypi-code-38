import unittest
import os
import sys
"""
This code will gather and run all the tests in this directory. Files with tests must start with the "test_" prefix.
"""

host = "localhost"
port = 5000
if len(sys.argv) >= 2:
    host = sys.argv[1]
if len(sys.argv) == 3:
    port = int(sys.argv[2])

unittest.TestCase.host = str(host)
unittest.TestCase.port = int(port)

loader = unittest.TestLoader()
testSuite = loader.discover(os.path.dirname(os.path.abspath(__file__)))

testRunner = unittest.TextTestRunner(verbosity=2)
testRunner.run(testSuite)
