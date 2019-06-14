from __future__ import (absolute_import, division, print_function, unicode_literals)

import pprint
import sys

import click


def clean_msg(msg):
    if isinstance(msg, (dict, list, set)):
        return pprint.pformat(msg)
    return '{}'.format(msg)


class Logger(object):

    @classmethod
    def info(cls, msg, exit=False):
        click.echo(clean_msg(msg))
        if exit:
            sys.exit(-1)

    @classmethod
    def warning(cls, msg, exit=False):
        click.secho(clean_msg(msg), fg='yellow')
        if exit:
            sys.exit(-1)

    @classmethod
    def debug(cls, msg, exit=False):
        click.secho(clean_msg(msg), fg='blue')
        if exit:
            sys.exit(-1)

    @classmethod
    def success(cls, msg, exit=False):
        click.secho(clean_msg(msg), fg='green')
        if exit:
            sys.exit(-1)

    @classmethod
    def code(cls, msg, exit=False):
        click.secho(clean_msg(msg), fg='cyan')
        if exit:
            sys.exit(-1)

    @classmethod
    def error(cls, msg, exit=True):
        click.secho(clean_msg(msg), fg='red')
        if exit:
            sys.exit(-1)

    @classmethod
    def title(cls, msg, exit=False):
        click.secho(clean_msg(msg), fg='white', bold=True)
        if exit:
            sys.exit(-1)
