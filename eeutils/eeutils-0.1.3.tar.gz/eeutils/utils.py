# -*- coding: utf-8 -*-
import psycopg2
import sys

import logging

import click

logger = logging.getLogger(__name__)


class with_cr(object):
    ok_params = ['dbname', 'database', 'user', 'password', 'host', 'port']

    def __init__(self, fnct):
        self.fnct = fnct

    @property
    def __name__(self):
        return self.fnct.__name__

    def __call__(self, *args, **kwargs):
        psyco_args = {k: v for k, v in kwargs.items() if k in self.ok_params}
        try:
            self.conn = psycopg2.connect(**psyco_args)
        except psycopg2.OperationalError as e:
            return self.fnct(*args, **kwargs)
        cursor = self.conn.cursor()
        kwargs['cr'] = cursor
        res = self.fnct(*args, **kwargs)
        cursor.close()
        self.conn.close()
        return res


_color_map = {
    'end': '\33[0m',
    'bold': '\33[1m',
    'italic': '\33[3m',
    'url': '\33[4m',
    'blink': '\33[5m',
    'blink2': '\33[6m',
    'selected': '\33[7m',

    'black': '\33[30m',
    'red': '\33[31m',
    'green': '\33[32m',
    'yellow': '\33[33m',
    'blue': '\33[34m',
    'purple': '\33[35m',
    'beige': '\33[36m',
    'white': '\33[37m',
}


def colorize(text, colors):
    assert isinstance(text, str)
    if isinstance(colors, str):
        colors = [colors]
    assert all([color in _color_map for color in colors])
    new_text = text
    for color in colors:
        new_text = _color_map[color] + new_text + _color_map['end']
    return new_text
    # return '%s%s%s' % (_color_map[color], text, _color_map['end'])


class manage_error(object):
    def __init__(self, fnct):
        self.fnct = fnct

    @property
    def __name__(self):
        return self.fnct.__name__

    def __call__(self, *args, **kwargs):
        res = False
        try:
            res = self.fnct(*args, **kwargs)
        except BaseException as err:
            click.secho("Error!", fg='red', blink=True, bold=True)
            click.echo("\n")
            click.echo(str(err))
            sys.exit(1)
        return res
