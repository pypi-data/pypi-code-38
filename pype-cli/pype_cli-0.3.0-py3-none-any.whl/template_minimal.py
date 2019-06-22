# -*- coding: utf-8 -*-
"""Not documented yet."""

import click

from pype.core import fname_to_name


@click.command(name=fname_to_name(__file__), help=__doc__)
def main():
    """Script's main entry point."""
    pass
