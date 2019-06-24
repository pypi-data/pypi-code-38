"""Docker-Compose down module."""
from typing import List

import click

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus
from megalus.utils import get_path


@click.command()
@click.option('--remove-all', is_flag=True)
@click.argument('projects', nargs=-1)
@click.pass_obj
def down(meg: Megalus, projects: List[str], remove_all: bool) -> None:
    """Down compose project.

    :param meg: Megalus instance
    :param projects: projects to down
    :param remove_all: remove image and containers too
    :return: None
    """
    options = ["rmi all", "volumes", "remove-orphans"] if remove_all else None

    projects_to_run = projects if projects else meg.config_data['compose_projects'].keys()

    for project_informed in projects_to_run:
        project_data = meg.find_project(project_informed)
        service_data = {
            'compose_files': project_data['files'],
            'working_dir': get_path(project_data['path'], meg.base_path),
            'compose_project': project_data,
            'all_compose_data': {}
        }
        run_compose_command(
            meg,
            action="down",
            service_data=service_data,
            options=options,
            all_services=True
        )
