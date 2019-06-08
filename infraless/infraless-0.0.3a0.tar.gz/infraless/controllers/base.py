#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
infraless/controllers/base.py

"""

from cement import Controller, ex
from cement.utils.version import get_version_banner

from ..core.version import get_version

VERSION_BANNER = """
Framework to build automated web platforms %s
%s
""" % (get_version(), get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Framework to build automated web platforms'

        # text displayed at the bottom of --help output
        epilog = 'Usage: infraless command <subcommand> <args>'

        # controller level arguments. ex: 'infraless --version'
        arguments = [
            # add a version banner
            (['-v', '--version'], {
                'action': 'version',
                'version': VERSION_BANNER
            }),
        ]

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()

    @ex(
        help='test command',

        # sub-command level arguments. ex: 'infraless command1 --foo bar'
        arguments=[
            # add a sample foo option under subcommand namespace
            (['-f', '--foo'], {
                'help': 'notorious foo option',
                'action': 'store',
                'dest': 'foo'
            }),
        ],
    )
    def test(self):
        """
        CLI test command.
        """

        data = {
            'foo': 'bar',
        }

        # do something with arguments
        if self.app.pargs.foo is not None:
            data['foo'] = self.app.pargs.foo
        self.app.render(data, 'test.jinja2')
