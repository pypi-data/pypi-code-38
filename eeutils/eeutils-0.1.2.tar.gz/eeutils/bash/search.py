# -*- coding: utf-8 -*-
import click

from ..main import bash


@bash.command()
@click.argument('pattern')
@click.option('-f', '--file-type',
              help="File extension.")
def search(pattern):
    """
    Preconfigured grep to faster typing.
    """
