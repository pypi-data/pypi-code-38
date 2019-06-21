# -*- coding: utf-8 -*-
import click  # noqa

from ..main import git


@git.command()
def branchrm():
    """
    Remove merged branches
    """
    pass
