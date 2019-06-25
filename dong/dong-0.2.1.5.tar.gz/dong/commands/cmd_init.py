import click

from dong.project import init_project

@click.command()
def command():
    """Create a new ML project in an existing directory."""
    init_project()
