# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from collections import namedtuple
from contextlib import contextmanager
from io import StringIO

import mock

from linecook import cli


FakeOutputs = namedtuple('FakeOutputs', ['print_', 'stdout'])
FakeIO = namedtuple('FakeIO', ['stdin', 'stdout'])


class TestBuildParser:

    def test_no_inputs(self):
        args = create_linecook_args([])
        assert args.recipe == 'default'
        assert args.text is None
        assert args.text_stream == sys.stdin

    def test_custom_recipe(self):
        args = create_linecook_args(['python'])
        assert args.recipe == 'python'

    def test_custom_text(self):
        args = create_linecook_args(['-t', 'Hello world'])
        assert args.text == 'Hello world'


class TestRun:

    def test_custom_text(self):
        input_text = 'Hello world'
        args = create_linecook_args(['identity', '-t', input_text])

        with mock_outputs() as fake_outputs:
            cli.run(args)

        fake_outputs.print_.assert_called_once_with(input_text)

    def test_stdin(self):
        input_text = u'Hello world'

        with mock.patch.object(cli, 'sys') as fake_sys:
            fake_sys.stdin = StringIO(input_text)
            args = create_linecook_args(['identity'])

            with mock_outputs() as fake_outputs:
                cli.run(args)

        fake_outputs.stdout.write.assert_called_once_with(input_text)

    def test_list_recipes(self):
        with mock_linecook_config({'recipes': {'my-recipe': []}}):
            args = create_linecook_args(['--list-recipes'])
            with mock_outputs() as fake_outputs:
                cli.run(args)

        fake_outputs.print_.assert_has_calls([
            mock.call('Available recipes:'),
            mock.call('- my-recipe'),
        ])

    def test_recipe_not_found(self):
        with mock_linecook_config({'recipes': {'my-recipe': []}}):
            args = create_linecook_args(['does-not-exist'])
            with mock_outputs() as fake_outputs:
                cli.run(args)

        fake_outputs.print_.assert_has_calls([
            mock.call(cli.recipe_not_found_msg('does-not-exist')),
            mock.call('Available recipes:'),
            mock.call('- my-recipe'),
        ])


class TestMain:

    def test_main(self):
        args = create_linecook_args()

        with mock.patch.object(cli, 'run') as fake_run:
            cli.main()

        fake_run.assert_called_once_with(args)


@contextmanager
def mock_outputs(module=cli):
    with mock.patch.object(module, 'print') as fake_print:
        with mock.patch.object(module.sys, 'stdout') as fake_stdout:
            yield FakeOutputs(print_=fake_print, stdout=fake_stdout)


@contextmanager
def mock_linecook_config(config_dict):
    with mock.patch.object(cli.config, 'load_config') as fake_load_config:
        linecook_config = cli.config.LineCookConfig([config_dict])
        fake_load_config.return_value = linecook_config
        yield linecook_config


def create_linecook_args(arg_list=()):
    parser = cli.build_parser()
    return parser.parse_args(arg_list)
