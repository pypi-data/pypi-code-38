from .version import __version__
import click

@click.command(help='Show the current version of the CLI.')
def version():
    click.echo('Lumavate CLI Version: {}'.format(__version__))
