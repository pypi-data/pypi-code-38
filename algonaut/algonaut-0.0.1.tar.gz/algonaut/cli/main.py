from algonaut.settings import settings
from algonaut.cli import commands

import click
import os
import logging

@click.group()
@click.option('-v', '--verbose', count=True, default=2)
def algonaut(verbose):
    settings.setup_logging(verbose)
    settings.initialize()

for command in commands:
    algonaut.add_command(command)

def main():
    for plugin in settings.get('plugins',{}):
        config = settings.load_plugin_config(plugin)
        if 'commands' in config:
            for command in config['commands']:
                algonaut.add_command(command)
    algonaut()

if __name__ == '__main__':
    main()
