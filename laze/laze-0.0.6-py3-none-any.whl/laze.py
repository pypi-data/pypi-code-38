#!/usr/bin/env python3

import os
import click

from click_default_group import DefaultGroup

from .generate import generate
from .build import build
from .create import create


@click.group(cls=DefaultGroup, default="build", default_if_no_args=True)
@click.option("--chdir", "-C", type=click.STRING)
def cli(chdir):
    if chdir:
        os.chdir(chdir)


cli.add_command(generate)
cli.add_command(build)
cli.add_command(create)
