# -*- coding: utf-8 -*-
"""Unregister an existing pype plugin."""


import click

from pype.core import PypeCore, fname_to_name
from pype.util.cli import print_success, print_warning


@click.command(name=fname_to_name(__file__), help=__doc__)
@click.option('--name', '-n', help='Plugin module name',
              metavar='NAME', required=True)
def main(name):
    """Script's main entry point."""
    # Try to load the module to verify the configuration
    core = PypeCore()
    config_json = core.get_config_json()
    new_plugins = [
        plugin for plugin in config_json['plugins']
        if plugin['name'] != name
    ]
    if config_json['plugins'] == new_plugins:
        print_warning('Plugin "{}" not found. Nothing to do.'.format(name))
        return
    config_json['plugins'] = new_plugins
    core.set_config_json(config_json)
    print_success('Plugin "{}" successfully unregistered.'.format(name))
