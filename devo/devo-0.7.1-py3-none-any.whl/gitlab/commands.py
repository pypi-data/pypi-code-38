import click

from .utils import sync_variables_to_gitlab


@click.group()
def gitlab():
    pass


@gitlab.command()
def sync():
    sync_variables_to_gitlab()
