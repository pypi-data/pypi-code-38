import click

from .create.commands import create
from .kube.commands import kube
from .gitlab.commands import gitlab
from .generate.commands import generate


@click.group()
def cli():
    pass


cli.add_command(create)
cli.add_command(kube)
cli.add_command(gitlab)
cli.add_command(generate)


if __name__ == '__main__':
    cli()
