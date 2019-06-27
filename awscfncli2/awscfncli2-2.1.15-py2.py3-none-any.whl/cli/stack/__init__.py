#  -*- encoding: utf-8 -*-

import click
from ..main import cfn_cli
from ...config import ConfigError

@cfn_cli.group()
@click.pass_context
def stack(ctx):
    """Stack operations."""
    pass
