# -*- coding: utf-8 -*-
"""Uninstall pype's autocompletion and aliases."""

import click

from pype.core import PypeCore, fname_to_name
from pype.util.cli import print_success


@click.command(name=fname_to_name(__file__), help=__doc__)
def main():
    """Script's main entry point."""
    core = PypeCore()
    core.uninstall_from_shell()
    print_success('Done. Please source your rc-file or open a new shell.')
