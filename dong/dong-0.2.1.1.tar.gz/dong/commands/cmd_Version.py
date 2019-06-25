import click
import os
import dong
import pkg_resources 

version = pkg_resources.require("dong")[0].version
@click.command(help='Print version and exit.', add_help_option=False)
def command():
    click.secho("dong " + version, fg='green')