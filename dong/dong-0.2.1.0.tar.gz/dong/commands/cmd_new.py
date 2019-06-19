import click

from dong.project import init_project

@click.command()
@click.argument('project')
def command(project):
    """Create a new ML project"""
    init_project(project)
