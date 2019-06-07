import os
import shlex
import subprocess as s
import uuid
from pprint import pformat

import click

from rebotics_sdk.cli.renderers import format_full_table
from rebotics_sdk.cli.utils import pass_rebotics_context
from rebotics_sdk.providers import ProviderHTTPClientException


def mean(arr):
    return sum(arr) / len(arr)


@click.group()
@click.version_option()
def main():
    """Collection of scripts for rebotics"""
    pass


@main.command()
@click.argument('container')
@click.argument('volume')
def fix_pycharm(container, volume):
    with s.Popen(shlex.split("docker ps -a --format '{{.Names}}'"), stdout=s.PIPE) as proc:
        containers = proc.stdout.read().decode('utf-8').split('\n')
        assert container in containers, 'Container should exist'

    # save helpers to the tmp folder
    tmp_folder = '/tmp/helper_folder_%s' % uuid.uuid4()
    os.system('docker cp {container}:/opt/.pycharm_helpers {tmp_folder}'.format(
        container=container,
        tmp_folder=tmp_folder
    ))

    # assign new container with attached volume
    helper_random_name = 'helper_%s' % uuid.uuid4()
    os.system('docker run -v {target_volume}:/opt/.pycharm_helpers --name {name} busybox true'.format(
        target_volume=volume,
        name=helper_random_name,
    ))

    os.system('docker cp {tmp_folder} {name}:/opt/.pycharm_helpers'.format(
        tmp_folder=tmp_folder,
        name=helper_random_name
    ))

    # Cleanup
    os.system('docker rm -f {helper_random_name}'.format(helper_random_name=helper_random_name))
    os.system('rm -rf {tmp_folder}'.format(tmp_folder=tmp_folder))
    click.echo('Finished')


@main.command()
def fix_pycharm_clean():
    """
    This command fixes all pycharm related volumes and merges the helpers folder to it.
    This is in case when you update pycharm and run with debugger, but it yields error:
    python: can't open file '/opt/.pycharm_helpers/pydev/pydevd.py': [Errno 2] No such file or directory
    """

    def find_pycharm_helpers_folders():
        for dirpath, dirnames, filenames in os.walk(os.path.expanduser('~')):
            if 'PyCharm' in dirpath:
                if '/helpers' in dirpath and '/helpers/' not in dirpath:  # get only the top folder
                    if 'pydev' in dirnames:
                        yield dirpath

    helper_folder = ''
    for path in find_pycharm_helpers_folders():
        helper_folder = path
        break
    click.echo('Using helper folder: {helper_folder}'.format(
        helper_folder=helper_folder
    ))

    with s.Popen(shlex.split("docker volume ls --format '{{ .Name }}'"), stdout=s.PIPE) as proc:
        volumes = proc.stdout.read().decode('utf-8').split('\n')

    for volume in volumes:
        if 'helpers' not in volume:
            continue
        click.echo('Fixing pycharm_helpers for {volume}')
        # assign new container with attached volume
        container = 'helper_%s' % uuid.uuid4()
        os.system('docker run -v {volume}:/opt/.pycharm_helpers --name {container} busybox true'.format(
            volume=volume,
            container=container
        ))
        os.system('docker cp {helper_folder}/. {container}:/opt/.pycharm_helpers/'.format(
            helper_folder=helper_folder,
            container=container
        ))

        # Cleanup
        os.system('docker rm -f {container}'.format(container=container))
    click.echo('Finished')


@main.command()
def install_bash_completion():
    path = os.path.expanduser('~/.bashrc')

    with open(path, 'a') as bashrc:
        commands = [
            '# Rebotics scripts autocomplete scripts',
            '# After you uninstall rebotics-scripts, please consider to delete this too',
            'eval "$(_RETAILER_COMPLETE=source retailer)"',
            'eval "$(_ADMIN_COMPLETE=source admin)"',
            'eval "$(_DATASET_COMPLETE=source dataset)"',
            'eval "$(_REBOTICS_COMPLETE=source rebotics)"',
        ]
        for command in commands:
            bashrc.write(command + "\n")

    click.edit(filename=path)


@click.command()
@pass_rebotics_context
def shell(ctx):
    """Opens interactive IPython shell """
    try:
        from IPython import start_ipython
        start_ipython(
            argv=[],
            user_ns={
                'provider': ctx.provider,
                'ctx': ctx,
            }
        )
    except ImportError:
        click.echo('You need to install rebotics_sdk[shell] and you also required to use Python3.5+')


@click.command()
@pass_rebotics_context
def roles(ctx):
    """List available roles to use"""
    config = ctx.config
    if ctx.format == 'json':
        click.echo(pformat(config.config, indent=2))
    elif ctx.format == 'id':
        for key, value in config.config.items():
            click.echo(key)
    elif ctx.format == 'table':
        role_configurations = []
        for key, value in config.config.items():
            data = value
            data['role'] = key
            role_configurations.append(data)
        click.echo(format_full_table(role_configurations, 100))


@click.command()
@click.option('-h', '--host', help='App host', prompt=True)
@click.option('-u', '--user', prompt=True, )
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=False)
@pass_rebotics_context
def configure(ctx, user, password, host):
    """Fetch token, save it and use the role of it"""
    provider = ctx.provider_class(host=host)
    ctx.update_configuration(
        host=host,
    )
    try:
        response = provider.token_auth(user, password)
    except ProviderHTTPClientException:
        click.echo('Failed to login')
        return

    ctx.update_configuration(
        host=host,
        **response
    )
    click.echo(response, err=True)
    click.echo('Saved configuration for {} in {}'.format(ctx.key, ctx.config.filepath))
