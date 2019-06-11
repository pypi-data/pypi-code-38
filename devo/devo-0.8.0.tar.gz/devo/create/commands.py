import os
from pathlib import Path
from urllib.parse import urlparse
import gitlab

import click

from devo.generate.utils import generate_project, generate_gitlab_ci, generate_k8s, generate_skaffold
from devo.gitlab.utils import push_credentials_env

from .utils import git_init, git_get_global_user, git_add_remote_origin, git_set_local_user, git_set_local_email, \
    git_get_global_email


@click.group()
def create():
    pass


@create.command()
@click.argument('project_name')
def package(project_name):
    """Not implemented. Placeholder for possible future template types."""
    click.echo('Not implemented')


@create.command()
@click.argument('project_name')
def docker(project_name):
    """Not implemented. Placeholder for possible future template types."""
    click.echo('Not implemented')


@create.command()
@click.argument('project_name')
def web(project_name):
    """Generate a web-based project."""
    if (Path.cwd() / project_name).exists():
        click.secho(f'Directory {project_name} exists already')

    click.echo(f'Starting project {project_name}')
    author_name = click.prompt('Local Git user name', default=git_get_global_user())
    author_email = click.prompt('Local Git email', default=git_get_global_email())

    while True:
        gitlab_url = click.prompt('GitLab Server', default='https://gitlab.com')
        gitlab_user = click.prompt('GitLab User')
        gitlab_token = click.prompt('GitLab Token')

        click.echo(f'Checking credentials for {gitlab_url}')
        try:
            gl = gitlab.Gitlab(gitlab_url, gitlab_token)
            gl.auth()
            break
        except gitlab.GitlabError as e:
            click.echo(f'GitLab error: {e}')
    click.echo(f'Authorization succeeded for {gitlab_url}')

    gitlab_host = urlparse(gitlab_url).netloc

    while True:
        gitlab_group = click.prompt('GitLab Group Name')
        try:
            click.echo(f'Checking group availability for {gitlab_group}')
            gitlab_group_obj = gl.groups.list(search=gitlab_group)[0]
            click.echo('Found existing group')
            break
        except IndexError:
            create_group = click.confirm(f'Could not find group {gitlab_group}. Create it?', default=True)
            if create_group:
                try:
                    click.echo(f'Creating group {gitlab_group}')
                    gitlab_group_obj = gl.groups.create({'name': gitlab_group, 'path': gitlab_group})
                    click.echo('Group created')
                    break
                except gitlab.GitlabError as e:
                    click.echo(f'GitLab error: {e}')
        except gitlab.GitlabError as e:
            click.echo(f'GitLab error: {e}')

    while True:
        gitlab_project_name = click.prompt('GitLab Project Name', default=project_name)
        try:
            click.echo(f'Creating project {gitlab_project_name} on {gitlab_url}')
            gitlab_project_obj = gl.projects.create({'name': gitlab_project_name, 'namespace_id': gitlab_group_obj.id})
            click.echo('Project created')
            break
        except gitlab.GitlabError as e:
            click.echo(f'GitLab error: {e}')

    use_gitlab_registry = click.confirm('Use GitLab Docker registry', default=True)
    if use_gitlab_registry:
        registry_url = click.prompt('Registry URL', default=f'registry.{gitlab_host}')
        registry_user = gitlab_user
        registry_password = gitlab_token
    else:
        registry_url = click.prompt('Registry URL', default='')
        registry_user = click.prompt('Registry User')
        registry_password = click.prompt('Registry Password')

    default_image_name = "/".join([registry_url, gitlab_group, project_name])
    registry_image = click.prompt('Docker Image Name', default=default_image_name)

    kube_url = click.prompt('k8s Cluster URL')
    kube_user = click.prompt('k8s User')
    kube_token = click.prompt('k8s Token')

    base_url = click.prompt('Base URL for deployments')

    use_database = click.confirm('Project needs database', default=False)

    ctx = {
        'project_name': project_name,
        'registry_image': registry_image,
        'registry_url': registry_url,
        'registry_user': registry_user,
        'registry_password': registry_password,
        'db': use_database,
        'gitlab_url': gitlab_url,
        'gitlab_group': gitlab_group,
        'gitlab_namespace_id': gitlab_group_obj.id,
        'gitlab_project': gitlab_project_name,
        'gitlab_project_id': gitlab_project_obj.id,
        'gitlab_user': gitlab_user,
        'gitlab_token': gitlab_token,
        'kube_url': kube_url,
        'kube_user': kube_user,
        'kube_token': kube_token,
        'base_url': base_url
    }

    click.echo(f'Generating project folder {project_name}')
    generate_project(ctx, False)

    click.echo(f'Switching into {project_name}')
    os.chdir(project_name)

    click.echo('Generating .gitlab-ci.yml')
    generate_gitlab_ci(ctx, False)

    click.echo('Generating k8s templates')
    generate_k8s(ctx, False)

    click.echo('Generating skaffold.yaml')
    generate_skaffold(ctx, False)

    click.echo('Creating CI variables')
    push_credentials_env()

    click.echo('Initializing Git')
    git_init()
    git_set_local_email(author_email)
    git_set_local_user(author_name)
    git_add_remote_origin(gitlab_host, gitlab_group, gitlab_project_name)
