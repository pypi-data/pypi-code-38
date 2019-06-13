# -*- coding: utf-8 -*-

"""Main module."""
import sys
import click

from typing import Any


def cube_primitive_test(x: int) -> int:
    return x * x


@click.command()
def main(args: Any = None) -> int:
    """Console script for trac_uni."""
    del args

    result_code = 0
    click.echo("Demo app for trac uni package")
    click.echo("2 x 2 = {}".format(cube_primitive_test(2)))
    return result_code


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
