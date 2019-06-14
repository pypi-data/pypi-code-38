#!/bin/env python3
import sys
import click

from typing import (
    List,
    Tuple,
    Dict,
    Optional
)

from conctl import getContainerRuntimeCtl


@click.group()
@click.option('--force-runtime', default=None,
              type=click.Choice(['docker', 'containerd']),
              help='Force a runtime')
@click.option('--verbose', default=False, is_flag=True,
              help='Print additional information')
@click.pass_context
def cli(context: object,
        force_runtime: Optional[str],
        verbose: bool) -> None:
    """
    Base for the CLI.

    :param context: Object
    :param force_runtime: String
    :param verbose: Boolean
    :return: None
    """
    context.obj = getContainerRuntimeCtl(force_runtime, pipe=False)

    if verbose:
        print('Runtime {} selected'.format(
            context.obj.runtime))


@cli.command()
@click.option('--name', required=True,
              help='Name the container')
@click.option('--mount', required=False, multiple=True,
              help='Pass mounts in format `host:container`')
@click.option('--env', required=False, multiple=True,
              help='Pass env vars in format `key=value`')
@click.option('--net-host', required=False, is_flag=True,
              help='Use host networking')
@click.option('--privileged', required=False, is_flag=True,
              help='Run privileged container')
@click.option('--rm', required=False, is_flag=True,
              help='Remove when container exits')
@click.argument('image', required=True)
@click.argument('command', required=False)
@click.argument('args', required=False, nargs=-1)
@click.pass_obj
def run(ctl: object,
        name: str,
        mount: Tuple[str],
        env: Tuple[str],
        net_host: bool,
        privileged: bool,
        rm: bool,
        image: str,
        command: str,
        args: Tuple[str]) -> None:
    """
    Run a container.

    :return: None
    """
    mounts: Dict[str, str] = {}
    for m in mount:
        s: List[str] = m.split(':')
        try:
            mounts[s[0]] = s[1]
        except IndexError:
            sys.exit('{} is not a valid arg for mount'.format(s))

    environment: Dict[str, str] = {}
    for e in env:
        s: List[str] = e.split('=')
        try:
            environment[s[0]] = s[1]
        except IndexError:
            sys.exit('{} is not a valid arg for env'.format(s))

    ctl.run(
        name=name,
        image=image,
        mounts=mounts,
        environment=environment,
        net_host=net_host,
        privileged=privileged,
        remove=rm,
        command=command,
        args=args
    )


@cli.command()
@click.argument('container_ids', required=False, nargs=-1)
@click.pass_obj
def delete(ctl: object,
           container_ids: Tuple[str]) -> None:
    """
    Delete containers.

    :return: None
    """
    ctl.delete(*container_ids)


@cli.command()
@click.option('--username', required=False,
              help='Registry username')
@click.option('--password', required=False,
              help='Registry password')
@click.argument('urls', required=True, nargs=-1)
@click.pass_obj
def pull(ctl: object,
         username: Optional[str],
         password: Optional[str],
         urls: List[str]) -> None:
    """
    Pull images.

    :return: None
    """
    ctl.pull(
        urls,
        username=username,
        password=password
    )


@cli.command()
@click.argument('path', required=True)
@click.pass_obj
def load(ctl: object,
         path: str) -> None:
    """
    Load an image.

    :return: None
    """
    ctl.load(
        path
    )


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
