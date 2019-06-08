# -*- coding: utf-8 -*-

"""Utility methods for mash client cli endpoints."""

# Copyright (c) 2018 SUSE LLC
#
# This file is part of mash_client. mash_client provides a command line
# utility for interfacing with a MASH server.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import click
import json
import logging
import os
import requests
import sys
import yaml

from collections import ChainMap
from contextlib import contextmanager, suppress
from textwrap import TextWrapper

from mash_client.mash_client_exceptions import MashClientException

default_config = os.path.expanduser('~/.config/mash_client/config.yaml')
defaults = {
    'config': default_config,
    'host': 'http://127.0.0.1',
    'log_level': logging.INFO,
    'no_color': False,
    'verify': True
}
EC2_PARTITIONS = ('aws', 'aws-cn', 'aws-us-gov')
SUPPORTED_CLOUDS = ('azure', 'ec2', 'gce')


def echo_dict(
    data, no_color, key_color='green', spaces=None, value_color='blue'
):
    """
    Echoes a dictionary pretty-print style to terminal.
    """
    if not spaces:
        spaces = get_max_key(data)

    for key, value in data.items():
        title = '{spaces}{key}:  '.format(
            spaces=' ' * (spaces - len(key)),
            key=key
        )
        wrapper = TextWrapper(
            width=(82 - spaces),
            subsequent_indent=' ' * (spaces + 3)
        )

        click.echo(
            ''.join([
                style_string(title, no_color, fg=key_color),
                wrapper.fill(style_string(value, no_color, fg=value_color))
            ])
        )


def echo_style(message, no_color, fg='yellow'):
    """
    Echo stylized output to terminal depending on no_color.
    """
    if no_color:
        click.echo(message)
    else:
        click.secho(message, fg=fg)


def get_config(cli_context):
    """
    Process mash client config.

    Use ChainMap to build config values based on
    command line args, config and defaults.
    """
    config_path = cli_context['config'] or default_config

    config_values = {}
    with suppress(Exception):
        with open(config_path) as config_file:
            config_values = yaml.safe_load(config_file)

    cli_values = {
        key: value for key, value in cli_context.items() if value is not None
    }
    data = ChainMap(cli_values, config_values, defaults)

    if 'port' in data:
        data['url'] = ':'.join([data['host'], str(data['port'])])
    else:
        data['url'] = data['host']

    return data


def get_max_key(data):
    """
    Get the max key length from dictionary.
    """
    return max(map(len, data))


@contextmanager
def handle_errors(log_level, no_color):
    """
    Context manager to handle exceptions and echo error msg.
    """
    try:
        yield
    except Exception as error:
        if log_level == logging.DEBUG:
            raise

        echo_style(
            "{}: {}".format(type(error).__name__, error),
            no_color,
            fg='red'
        )
        sys.exit(1)


def handle_request(config_data, endpoint, job_data=None):
    """
    Post request based on endpoint and data.

    If response is successful echo the dictionary status.
    Otherwise raise exception.
    """
    response = requests.post(
        ''.join([config_data['url'], endpoint]),
        data=None if not job_data else json.dumps(job_data),
        verify=config_data['verify']
    )

    if response.status_code == 200:
        echo_dict(response.json(), config_data['no_color'])
    elif response.status_code == 400:
        raise MashClientException(response.json()['error'])
    else:
        response.raise_for_status()


def style_string(message, no_color, fg='yellow'):
    """
    Add color style to string if no_color is False.
    """
    if no_color:
        return message
    else:
        return click.style(message, fg=fg)
