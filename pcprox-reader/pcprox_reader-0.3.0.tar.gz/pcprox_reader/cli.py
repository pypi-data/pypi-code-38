# -*- coding: utf-8 -*-

"""Console script for pcprox_reader."""
import sys
import click
from .cardreader import CardReader


@click.command()
def main(args=None):
    """Console script for pcprox_reader."""
    click.echo(" Swipe a badge on the pcProx Reader ")
    click.echo(" <<< Ctrl+C to quit >>> ")
    reader = CardReader()
    reader.swipe_loop()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
