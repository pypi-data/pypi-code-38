#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import click

class Logger():
    def __init__(self, *args, **kwargs):
        pass

    def info(self, *msg):
        color = 'cyan'
        message = ' '.join(msg)
        click.echo(click.style('[INFO] ', fg=color) + message)

    def debug(self, *msg, with_color=False):
        color = 'yellow'
        message = ' '.join(msg)
        if with_color:
            message = click.style(message, fg=color)
        click.echo(click.style('[DBUG] ', fg=color) + message)

    def error(self, *msg, with_color=False):
        color = 'red'
        message = ' '.join(msg)
        if with_color:
            message = click.style(message, fg=color)
        click.echo(click.style('[ERRO] ', fg=color) + message)

    def warn(self, *msg, with_color=False):
        color = 'magenta'
        message = ' '.join(msg)
        if with_color:
            message = click.style(message, fg=color)
        click.echo(click.style('[WARN] ', fg=color) + message)



