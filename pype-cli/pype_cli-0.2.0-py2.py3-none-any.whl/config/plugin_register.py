# -*- coding: utf-8 -*-
"""Register a new pype plugin."""


import getpass
from os import mkdir
from os.path import isdir, join

import click

from pype.core import PypeCore, load_module
from pype.exceptions import PypeException
from pype.util.iotools import resolve_path


@click.command(help=__doc__)
@click.option('--name', '-n', help='Plugin module name', required=True)
@click.option('--path', '-p', help='Module directory', required=True)
@click.option('--create', '-c', help='Create on the fly', is_flag=True)
@click.option('--user-only', '-u', help='Just for current user', is_flag=True)
def main(name, path, create, user_only):
    """Script's main entry point."""
    if create:
        _create_on_the_fly(name, path)
    # Try to load the module to verify the configuration
    try:
        module = load_module(name, path)
    except PypeException:
        print('Could not find a python module "{}" at {}'
              .format(name, path))
        exit(1)
    core = PypeCore()
    config_json = core.get_config_json()
    users = [getpass.getuser()] if user_only else []
    config_json['plugins'].append({
        'name': module.__name__,
        'path': path,
        'users': users
    })
    core.set_config_json(config_json)
    print('Plugin "{}" successfully registered.'.format(name))


def _create_on_the_fly(name, path):
    abspath = resolve_path(path)
    if not isdir(abspath):
        print('Path {} does not point to a directoy.'.format(abspath))
        exit(1)
    plugin_dir = join(abspath, name)
    if isdir(plugin_dir):
        print('Path {} already exists.'.format(abspath))
        exit(1)
    plugin_init_file = join(plugin_dir, '__init__.py')
    mkdir(plugin_dir)
    with open(plugin_init_file, 'w+') as init:
        init.write('"""Not documented yet."""\n')
    print('Plugin "{}" successfully created at {}'.format(
        name, abspath))


if __name__ == '__main__':
    main()
