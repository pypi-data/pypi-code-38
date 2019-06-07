# -*- coding: utf-8 -*-

"""Console script for fifteenrock."""
import sys
import click
from fifteenrock.cli.compute import commands as compute_commands


@click.group('compute')
def main():
    pass


main.add_command(compute_commands.compute)

# @click.command()
# def main(args=None):
#     """Console script for fifteenrock."""
#     click.echo("Replace this message by putting your code into "
#                "fifteenrock.cli.main")
#     click.echo("See click documentation at http://click.pocoo.org/")
#     return 0
#

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
