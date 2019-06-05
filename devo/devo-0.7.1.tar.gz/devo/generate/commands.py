import click

from .utils import generate_gitlab_ci, generate_skaffold, generate_k8s
from devo.config import config_to_context
from devo.exceptions import OverwriteException


@click.group()
def generate():
    pass


@generate.command()
@click.option('--force', is_flag=True, default=False)
def gitlab_ci(force):
    ctx = config_to_context()
    try:
        generate_gitlab_ci(ctx, force)
    except OverwriteException as e:
        click.echo(e)


@generate.command()
@click.option('--force', is_flag=True, default=False)
def skaffold(force):
    ctx = config_to_context()
    try:
        generate_skaffold(ctx, force)
    except OverwriteException as e:
        click.echo(e)


@generate.command()
@click.option('--force', is_flag=True, default=False)
def k8s(force):
    ctx = config_to_context()
    try:
        generate_k8s(ctx, force)
    except OverwriteException as e:
        click.echo(e)


