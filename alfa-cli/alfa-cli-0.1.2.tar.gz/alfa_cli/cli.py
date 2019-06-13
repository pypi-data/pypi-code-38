import sys
import click
import traceback

from alfa_cli import __version__
from alfa_cli.common.logger import Logger
from alfa_cli.commands import configure, secrets, algorithm, resource


#


@click.group(name="alfa", context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-v", "--verbose", is_flag=True, default=None, help="Enable verbose outputs.")
@click.option("-p", "--pretty", is_flag=True, default=None, help="Pretty print the results.")
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx=None, verbose=None, pretty=None):
    """CLI tools for working with ALFA (Algorithm Factory)."""

    logger = Logger(verbose=verbose, pretty=pretty)
    ctx.obj = {"pretty": pretty, "logger": logger}


cli.add_command(configure.configure)
cli.add_command(algorithm.algorithm)
cli.add_command(secrets.secrets)
cli.add_command(resource.resource)


#


def main():
    try:
        cli()
    except Exception as err:
        Logger.error(err)
