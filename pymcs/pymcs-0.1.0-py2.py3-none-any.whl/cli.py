# -*- coding: utf-8 -*-

"""Console script for pymcs."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for pymcs."""
    click.echo("Replace this message by putting your code into "
               "pymcs.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
