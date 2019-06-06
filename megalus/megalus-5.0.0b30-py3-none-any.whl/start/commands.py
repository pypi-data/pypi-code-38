"""Megalus Start Command."""
import click

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus
from megalus.utils import get_path


@click.command()
@click.argument('projects', nargs=-1, required=True)
@click.pass_obj
def start(meg: Megalus, projects: str) -> None:
    """Start selected projects.

    :param meg: Megalus instance
    :param projects: Megalus projects to be started up
    :return: None
    """
    for project_informed in projects:
        project_data = meg.find_project(project_informed)
        service_data = {
            'compose_files': project_data['files'],
            'working_dir': get_path(project_data['path'], meg.base_path),
            'compose_project': project_data,
            'all_compose_data': {}
        }
        run_compose_command(
            meg,
            action="up -d",
            options=['remove-orphans'],
            service_data=service_data,
            all_services=True
        )
