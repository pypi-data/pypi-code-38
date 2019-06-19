#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import yaml
import click
import pkg_resources
import conda_build.api

from . import bdt
from ..build import conda_arch, make_conda_config, get_docserver_setup, \
    get_env_directory
from ..constants import CONDA_BUILD_CONFIG, CONDA_RECIPE_APPEND, \
    SERVER, MATPLOTLIB_RCDIR, BASE_CONDARC
from ..bootstrap import set_environment, get_channels

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Tests conda package:

\b
     $ bdt test -vv /path/to/conda-package-v1.0.0.tar.bz2


  2. Tests multiple conda packages, one after the other:

\b
     $ bdt test -vv /path/to/conda-package-v1.0.0.tar.bz2 /path/to/other-conda-package-v2.0.0.tar.bz2

''')
@click.argument('package', required=True, type=click.Path(file_okay=True,
  dir_okay=False, exists=True), nargs=-1)
@click.option('-r', '--condarc',
    help='Use custom conda configuration file instead of our own',)
@click.option('-m', '--config', '--variant-config-files', show_default=True,
    default=CONDA_BUILD_CONFIG, help='overwrites the path leading to ' \
        'variant configuration file to use')
@click.option('-a', '--append-file', show_default=True,
    default=CONDA_RECIPE_APPEND, help='overwrites the path leading to ' \
        'appended configuration file to use')
@click.option('-S', '--server', show_default=True, default=SERVER,
    help='Server used for downloading conda packages and documentation ' \
        'indexes of required packages')
@click.option('-g', '--group', show_default=True, default='bob',
    help='Group of packages (gitlab namespace) this package belongs to')
@click.option('-P', '--private/--no-private', default=False,
    help='Set this to **include** private channels on your build - ' \
        'you **must** be at Idiap to execute this build in this case - ' \
        'you **must** also use the correct server name through --server - ' \
        'notice this option has no effect to conda if you also pass --condarc')
@click.option('-X', '--stable/--no-stable', default=False,
    help='Set this to **exclude** beta channels from your build - ' \
        'notice this option has no effect if you also pass --condarc')
@click.option('-L', '--use-local/--no-use-local', default=False,
    help='Set this to **include** the locally built packages on the search ' \
        'list - notice this option has no effect if you also pass --condarc')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@click.option('-C', '--ci/--no-ci', default=False, hidden=True,
    help='Use this flag to indicate the build will be running on the CI')
@verbosity_option()
@bdt.raise_on_error
def test(package, condarc, config, append_file, server, group, private, stable,
    use_local, dry_run, ci):
  """Tests (pre-built) package through conda-build with stock configuration

  This command wraps the execution of conda-build so that you use the same
  conda configuration we use for our CI.  It always set
  ``--no-anaconda-upload``.
  """

  # if we are in a dry-run mode, let's let it be known
  if dry_run:
      logger.warn('!!!! DRY RUN MODE !!!!')
      logger.warn('Nothing will be really built')

  logger.debug('This package is considered part of group "%s" - tunning ' \
      'conda package and documentation URLs for this...', group)

  # get potential channel upload and other auxiliary channels
  channels = get_channels(public=(not private), stable=stable, server=server,
      intranet=ci, group=group)

  if condarc is not None:
    logger.info('Loading CONDARC file from %s...', condarc)
    with open(condarc, 'rb') as f:
      condarc_options = yaml.load(f, Loader=yaml.FullLoader)
  else:
    # use default and add channels
    all_channels = ['local'] if use_local else []
    all_channels += channels + ['defaults']
    condarc_options = yaml.load(BASE_CONDARC, Loader=yaml.FullLoader)
    logger.info('Using the following channels during build:\n  - %s',
        '\n  - '.join(all_channels))
    condarc_options['channels'] = all_channels

  conda_config = make_conda_config(config, None, append_file,
      condarc_options)

  set_environment('MATPLOTLIBRC', MATPLOTLIB_RCDIR)

  # setup BOB_DOCUMENTATION_SERVER environment variable (used for bob.extension
  # and derived documentation building via Sphinx)
  set_environment('DOCSERVER', server)
  doc_urls = get_docserver_setup(public=(not private), stable=stable,
      server=server, intranet=ci, group=group)
  set_environment('BOB_DOCUMENTATION_SERVER', doc_urls)

  arch = conda_arch()
  for p in package:
    logger.info('Testing %s at %s', p, arch)
    if not dry_run:
      conda_build.api.test(p, config=conda_config)
