# Compatibility imports
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

# System imports
import os
import unittest

# Local imports
from htpio.decorators import Countcalls
from htpio.decorators import Logger


LOGFILE = "../logs/test_decorators.log"


class TestDecorators(unittest.TestCase):
    """
    Unit test class for the framework decorators
    """

    def setUp(self):
        if os.path.isfile(LOGFILE):
            os.remove(LOGFILE)

    def tearDown(self):
        pass

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  test_countcalls : Function calls counter decorator
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_countcalls(self):
        """
        Call a function number of times and check if the decorator counter is
        returning the right number of calls
        """

        # Decorate
        @Countcalls
        def f():
            pass

        # Function under test
        count = 0
        for i in range(100):
            count = i + 1
            f()

        # Test 01 : Number of calls
        self.assertEqual(f.count(), count)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  test_logger : Error logging decorator
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_logger(self):
        """
        Decorates a function for logging by capturing the exceptions and
        writing them to a logger instance(stderr, file or other output device).
        """

        # Decorate
        @Countcalls
        @Logger(LOGFILE)
        def f():
            return 1 / 0

        # Function under test
        raised = False
        try:
            f()
        except Exception:
            raised = True
            Logger.log.info("Number of calls==[{0}]".format(f.count()))

        # Test 01 : Check if exception was generated
        self.assertIs(raised, True)

        # Test 02 : Check if log file exists
        logfile_exists = os.path.isfile(Logger.logfile)
        self.assertIs(logfile_exists, True)

        # Test 03 : Check if log file is not empty
        logfile_size = os.path.getsize(Logger.logfile)
        self.assertGreater(logfile_size, 0)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  MAIN PROGRAM
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testDecorators']
    unittest.main()
