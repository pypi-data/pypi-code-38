# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import csv
import datetime
import argparse
from unittest import TestCase
from six import StringIO

import six
# from sqlalchemy import func
from mock import patch, Mock
from fixture import TempIO

from rattail.commands import core
from rattail.db import Session, model
from rattail.db.auth import authenticate_user
from rattail.tests import DataTestCase


class TestArgumentParser(TestCase):

    def test_parse_args_preserves_extra_argv(self):
        parser = core.ArgumentParser()
        parser.add_argument('--some-optional-arg')
        parser.add_argument('some_required_arg')
        args = parser.parse_args([
                '--some-optional-arg', 'optional-value', 'required-value',
                'some', 'extra', 'args'])
        self.assertEqual(args.some_required_arg, 'required-value')
        self.assertEqual(args.some_optional_arg, 'optional-value')
        self.assertEqual(args.argv, ['some', 'extra', 'args'])


class TestDateArgument(TestCase):

    def test_valid_date_string_returns_date_object(self):
        date = core.date_argument('2014-01-01')
        self.assertEqual(date, datetime.date(2014, 1, 1))

    def test_invalid_date_string_raises_error(self):
        self.assertRaises(argparse.ArgumentTypeError, core.date_argument, 'invalid-date')


class TestCommand(TestCase):

    def test_initial_subcommands_are_sane(self):
        command = core.Command()
        self.assertTrue('filemon' in command.subcommands)

    def test_unicode(self):
        command = core.Command()
        command.name = 'some-app'
        self.assertEqual(six.text_type(command), 'some-app')
        
    def test_iter_subcommands_includes_expected_item(self):
        command = core.Command()
        found = False
        for subcommand in command.iter_subcommands():
            if subcommand.name == 'filemon':
                found = True
                break
        self.assertTrue(found)

    def test_print_help(self):
        command = core.Command()
        stdout = StringIO()
        command.stdout = stdout
        command.print_help()
        output = stdout.getvalue()
        stdout.close()
        self.assertTrue('Usage:' in output)
        self.assertTrue('Options:' in output)

    def test_run_with_no_args_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run()
            print_help.assert_called_once_with()

    def test_run_with_single_help_arg_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('help')
            print_help.assert_called_once_with()

    def test_run_with_help_and_unknown_subcommand_args_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('help', 'invalid-subcommand-name')
            print_help.assert_called_once_with()

    def test_run_with_help_and_subcommand_args_prints_subcommand_help(self):
        command = core.Command()
        fake = command.subcommands['fake'] = Mock()
        command.run('help', 'fake')
        fake.return_value.parser.print_help.assert_called_once_with()

    def test_run_with_unknown_subcommand_arg_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('invalid-command-name')
            print_help.assert_called_once_with()

    def test_stdout_may_be_redirected(self):
        class Fake(core.Subcommand):
            def run(self, args):
                self.stdout.write("standard output stuff")
                self.stdout.flush()
        command = core.Command()
        fake = command.subcommands['fake'] = Fake
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        out_path = tmp.putfile('out.txt', '')
        command.run('fake', '--config', config_path, '--stdout', out_path)
        with open(out_path) as f:
            self.assertEqual(f.read(), "standard output stuff")

    def test_stderr_may_be_redirected(self):
        class Fake(core.Subcommand):
            def run(self, args):
                self.stderr.write("standard error stuff")
                self.stderr.flush()
        command = core.Command()
        fake = command.subcommands['fake'] = Fake
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        err_path = tmp.putfile('err.txt', '')
        command.run('fake', '--config', config_path, '--stderr', err_path)
        with open(err_path) as f:
            self.assertEqual(f.read(), "standard error stuff")

    # # TODO: Figure out a better way to test this, or don't bother.
    # def test_noinit_flag_means_no_config(self):
    #     command = commands.Command()
    #     fake = command.subcommands['fake'] = Mock()
    #     command.run('fake', '--no-init')
    #     self.assertEqual(len(fake.return_value.config.files_requested), 0)


class TestSubcommand(TestCase):

    def test_add_parser_args_does_nothing(self):
        command = core.Command()
        subcommand = core.Subcommand(command)
        # Not sure this is really the way to test this, but...
        self.assertEqual(len(subcommand.parser._action_groups[0]._actions), 1)
        subcommand.add_parser_args(subcommand.parser)
        self.assertEqual(len(subcommand.parser._action_groups[0]._actions), 1)

    def test_run_not_implemented(self):
        command = core.Command()
        subcommand = core.Subcommand(command)
        args = subcommand.parser.parse_args([])
        self.assertRaises(NotImplementedError, subcommand.run, args)


# TODO: more broken tests..ugh.  these aren't very good or else i might bother
# fixing them...
# class TestFileMonitor(TestCase):

#     @patch('rattail.filemon.linux.start_daemon')
#     def test_start_daemon_with_default_args(self, start_daemon):
#         commands.main('filemon', '--no-init', 'start')
#         start_daemon.assert_called_once_with(None, None, True)

#     @patch('rattail.filemon.linux.start_daemon')
#     def test_start_daemon_with_explicit_args(self, start_daemon):
#         tmp = TempIO()
#         pid_path = tmp.putfile('test.pid', '')
#         commands.main('filemon', '--no-init', '--pidfile', pid_path, '--do-not-daemonize', 'start')
#         start_daemon.assert_called_once_with(None, pid_path, False)

#     @patch('rattail.filemon.linux.stop_daemon')
#     def test_stop_daemon_with_default_args(self, stop_daemon):
#         commands.main('filemon', '--no-init', 'stop')
#         stop_daemon.assert_called_once_with(None, None)

#     @patch('rattail.filemon.linux.stop_daemon')
#     def test_stop_daemon_with_explicit_args(self, stop_daemon):
#         tmp = TempIO()
#         pid_path = tmp.putfile('test.pid', '')
#         commands.main('filemon', '--no-init', '--pidfile', pid_path, 'stop')
#         stop_daemon.assert_called_once_with(None, pid_path)

#     @patch('rattail.commands.sys')
#     def test_unknown_platform_not_supported(self, sys):
#         tmp = TempIO()
#         stderr_path = tmp.putfile('stderr.txt', '')
#         sys.platform = 'bogus'
#         commands.main('--no-init', '--stderr', stderr_path, 'filemon', 'start')
#         sys.exit.assert_called_once_with(1)
#         with open(stderr_path) as f:
#             self.assertEqual(f.read(), "File monitor is not supported on platform: bogus\n")
