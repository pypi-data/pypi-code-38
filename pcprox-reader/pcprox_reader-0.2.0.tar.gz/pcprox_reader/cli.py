# -*- coding: utf-8 -*-

"""Console script for pcprox_reader."""
import sys
import click
from .pcprox_reader import CardReader


@click.command()
def main(args=None):
    """Console script for pcprox_reader."""
    click.echo("Replace this message by putting your code into "
               "pcprox_reader.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    reader = CardReader()
    reader.swipe_loop()
    sys.exit(main())  # pragma: no cover
