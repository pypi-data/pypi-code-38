# -*- coding: utf-8 -*-
"""Console script for udserver."""
import sys
import click
from udserver import udserver
import os


@click.command()
@click.option(
    '--storage', '-s', type=click.Path(exists=True), help='set storage folder')
def main(storage):
    udserver.app.config['STORAGE_FOLDER'] = os.path.abspath(storage)
    udserver.show_localip()
    udserver.app.run(host='0.0.0.0', debug=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
