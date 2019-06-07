"""Tests for the startup_log function."""
from argparse import Namespace
from unittest import TestCase

from mock import patch

from logging_toolbox.startup import startup_log


@patch('logging_toolbox.startup.logger')
class StartupLogTester(TestCase):
    """The startup_log tester."""
    def test_invalid_cleaner_function(self, mock_logger):
        """
        Tests whether the startup log function works even with invalid
        cleaner functions.

        Expected result:
        * The argument is printed unchanged.
        * A warning is logged at the end.
        """
        input_args = Namespace(arg1='1', arg2=2)
        cleaners = {'arg1': lambda v: v + 20}

        try:
            startup_log(input_args, cleaners=cleaners)
        except Exception:
            self.fail('Startup log failed catching cleaner errors!')

        mock_logger.info.assert_any_call('%-*s: %s', 5, 'arg1', '1')
        mock_logger.warning.assert_called_once()
