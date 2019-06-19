#!/usr/bin/env python

import os

import pkg_resources

import click
from click_plugins import with_plugins

from . import bdt


@with_plugins(pkg_resources.iter_entry_points('bdt.gitlab.cli'))
@click.group(cls=bdt.AliasedGroup)
def gitlab():
  """Commands for that interact with gitlab

  Commands defined here are supposed to interact with gitlab, and
  add/modify/remove resources on it directly.
  """
  pass
