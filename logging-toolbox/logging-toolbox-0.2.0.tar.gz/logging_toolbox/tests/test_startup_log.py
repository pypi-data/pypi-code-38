"""Tests for the startup_log function."""
from argparse import Namespace
from unittest import TestCase

from mock import MagicMock

from logging_toolbox.startup import startup_log, _get_version


class StartupLogTester(TestCase):
    """The startup_log tester."""
    def test_invalid_cleaner_function(self):
        """
        Tests whether the startup log function works even with invalid
        cleaner functions.

        Expected result:
        * The argument is printed unchanged.
        * A warning is logged at the end.
        """
        input_args = Namespace(arg1='1', arg2=2)
        cleaners = {'arg1': lambda v: v + 20}
        mock_logger = MagicMock()

        try:
            startup_log(input_args, cleaners=cleaners, logger=mock_logger)
        except Exception:
            self.fail('Startup log failed catching cleaner errors!')

        mock_logger.info.assert_any_call('%-*s: %s', 5, 'arg1', '1')
        mock_logger.warning.assert_called_once()

class VersionResolverTester(TestCase):
    """Tests the _get_version function"""
    def test_not_installed_module(self):
        """
        Tests the case when a module does not have a __version__
        attribute but is not installed. Most likely, this is the module
        you are currently working on.

        Expected result:
        * the version is 'UNKNOWN'
        * No exception is thrown
        """
        mock_module = MagicMock(__name__='mock_module')

        try:
            result = _get_version(mock_module)
        except Exception:
            self.fail('The _get_version function threw an exception!')

        self.assertEqual(result, 'UNKNOWN')
