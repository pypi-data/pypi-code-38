# -*- coding: utf-8 -*-
"""Print current pype version."""

import click

import pkg_resources

from pype.core import fname_to_name, get_pype_basepath


@click.command(name=fname_to_name(__file__), help=__doc__)
def main():
    """Script's main entry point."""
    base_path = get_pype_basepath()
    version = pkg_resources.get_distribution('pype-cli').version
    print('{} @ {}'.format(version, base_path))
