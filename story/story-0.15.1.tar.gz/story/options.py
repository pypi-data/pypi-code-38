# -*- coding: utf-8 -*-

import click


try:
    from . import cli

    _app = cli.get_app_name_from_yml()
except:
    _app = None


def app(allow_option=True):
    return click.option(
        '--app',
        '-a',
        default=_app,
        help=f'(required) [default: {_app}] app to run command against',
        callback=lambda context, p, app: cli.assert_project(
            context.command.name, app, _app, allow_option
        ),
    )
