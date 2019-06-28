""" Command line interface for the OnePanel Machine Learning platform

Entry point for command line interface.
"""

import click

from onepanel.commands.common import clone, download, push, timer_sync_output
from onepanel.utilities.original_connection import Connection

from onepanel.commands.datasets import datasets
from onepanel.commands.environments import environments
from onepanel.commands.instances import workspaces
from onepanel.commands.jobs import jobs
from onepanel.commands.login import login, login_with_token, logout
from onepanel.commands.machine_types import machine_types
from onepanel.commands.projects import projects
from onepanel.commands.volume_types import volume_types
from onepanel.constants import *

@click.group()
@click.version_option(version=CLI_VERSION, prog_name='Onepanel CLI')
@click.pass_context
def cli(ctx):
    conn = Connection()
    conn.load_credentials()

    ctx.obj['connection'] = conn


cli.add_command(login)
cli.add_command(login_with_token)
cli.add_command(logout)
cli.add_command(clone)
cli.add_command(download)
cli.add_command(push)
cli.add_command(projects)
cli.add_command(datasets)
cli.add_command(jobs)
cli.add_command(machine_types)
cli.add_command(environments)
cli.add_command(volume_types)
cli.add_command(workspaces)
cli.add_command(timer_sync_output)

# System commands 
try:
    from onepanel.commands.system import system
    
    cli.add_command(system)
except ImportError:
    pass


def main():
    return cli(obj={})


if __name__ == '__main__':
    cli(obj={})
