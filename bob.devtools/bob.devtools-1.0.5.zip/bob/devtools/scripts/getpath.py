#!/usr/bin/env python

import os

import click

from . import bdt
from ..release import get_gitlab_instance, download_path

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Get the file ``order.txt`` from bob.nightlies master branch:

     $ bdt gitlab getpath bob/bob.nightlies order.txt


  2. Get the file ``order.txt`` from a different branch ``2.x``:

     $ bdt gitlab getpath --ref=2.x bob/bob.nightlies order.txt


  3. Get the directory ``gitlab`` (and eventual sub-directories) from bob.admin, save outputs in directory ``_ci``:

     $ bdt gitlab getpath bob/bob.admin master gitlab _ci
''')
@click.argument('package')
@click.argument('path')
@click.argument('output', type=click.Path(exists=False), required=False)
@click.option('-r', '--ref', default='master', show_default=True,
    help='Download path from the provided git reference (may be a branch, tag or commit hash)')
@verbosity_option()
@bdt.raise_on_error
def getpath(package, path, output, ref):
    """Downloads files and directories from gitlab

    Files are downloaded and stored.  Directories are recursed and fully
    downloaded to the client.
    """

    if '/' not in package:
        raise RuntimeError('PACKAGE should be specified as "group/name"')

    gl = get_gitlab_instance()

    # we lookup the gitlab package once
    use_package = gl.projects.get(package)
    logger.info('Found gitlab project %s (id=%d)',
        use_package.attributes['path_with_namespace'], use_package.id)
    download_path(use_package, path, output, ref=ref)
