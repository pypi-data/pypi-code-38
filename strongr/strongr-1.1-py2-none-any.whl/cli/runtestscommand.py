from .wrapper import Command

import unittest

class RunTestsCommand(Command):
    """
    Runs the unit tests

    unittests:run
    """
    def handle(self):
        testsuite = unittest.TestLoader().discover('.')
        unittest.TextTestRunner(verbosity=1).run(testsuite)
