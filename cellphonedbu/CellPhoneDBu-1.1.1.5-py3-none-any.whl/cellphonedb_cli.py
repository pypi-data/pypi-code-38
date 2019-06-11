#!/usr/bin/env python3
import click

from cellphonedb.src.api_endpoints.terminal_api.method_terminal_api_endpoints import method_terminal_commands

@click.group()
def cli():
    pass


@cli.group()
def method():
    pass

method.add_command(method_terminal_commands.winsorizer)

if __name__ == '__main__':
    cli()
