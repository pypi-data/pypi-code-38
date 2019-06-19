#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import urllib.request

import yaml
import click
import pkg_resources
import conda_build.api

from . import bdt
from ..build import next_build_number, conda_arch, should_skip_build, \
    get_rendered_metadata, get_parsed_recipe, make_conda_config, \
    get_docserver_setup, get_env_directory, get_output_path
from ..constants import CONDA_BUILD_CONFIG, CONDA_RECIPE_APPEND, \
    SERVER, MATPLOTLIB_RCDIR, BASE_CONDARC
from ..bootstrap import set_environment, get_channels

from ..log import verbosity_option, get_logger, echo_normal
logger = get_logger(__name__)


@click.command(epilog='''
Examples:
  1. Rebuilds a recipe from one of our packages, checked-out at "bob/bob.extension", for python 3.6:

\b
     $ bdt rebuild -vv --python=3.6 bob/bob.extension/conda


  2. To rebuild multiple recipes, just pass the paths to them:

\b
     $ bdt rebuild -vv --python=3.6 path/to/recipe-dir1 path/to/recipe-dir2
''')
@click.argument('recipe-dir', required=False, type=click.Path(file_okay=False,
  dir_okay=True, exists=True), nargs=-1)
@click.option('-p', '--python', default=('%d.%d' % sys.version_info[:2]),
    show_default=True, help='Version of python to build the environment for')
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
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@click.option('-C', '--ci/--no-ci', default=False, hidden=True,
    help='Use this flag to indicate the build will be running on the CI')
@verbosity_option()
@bdt.raise_on_error
def rebuild(recipe_dir, python, condarc, config, append_file,
    server, group, private, stable, dry_run, ci):
  """Tests and rebuilds packages through conda-build with stock configuration

  This command wraps the execution of conda-build in two stages: first, from
  the original package recipe and some channel look-ups, it figures out what is
  the lastest version of the package available.  It downloads such file and
  runs a test.  If the test suceeds, then it proceeds to the next recipe.
  Otherwise, it rebuilds the package and uploads a new version to the channel.
  """

  # if we are in a dry-run mode, let's let it be known
  if dry_run:
      logger.warn('!!!! DRY RUN MODE !!!!')
      logger.warn('Nothing will be really built')

  recipe_dir = recipe_dir or [os.path.join(os.path.realpath('.'), 'conda')]

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
    condarc_options = yaml.load(BASE_CONDARC, Loader=yaml.FullLoader)
    logger.info('Using the following channels during build:\n  - %s',
        '\n  - '.join(channels + ['defaults']))
    condarc_options['channels'] = channels + ['defaults']

  # dump packages at base environment
  prefix = get_env_directory(os.environ['CONDA_EXE'], 'base')
  condarc_options['croot'] = os.path.join(prefix, 'conda-bld')

  conda_config = make_conda_config(config, python, append_file,
      condarc_options)

  set_environment('MATPLOTLIBRC', MATPLOTLIB_RCDIR)

  # setup BOB_DOCUMENTATION_SERVER environment variable (used for bob.extension
  # and derived documentation building via Sphinx)
  set_environment('DOCSERVER', server)
  doc_urls = get_docserver_setup(public=(not private), stable=stable,
      server=server, intranet=ci, group=group)
  set_environment('BOB_DOCUMENTATION_SERVER', doc_urls)

  arch = conda_arch()

  for d in recipe_dir:

    if not os.path.exists(d):
      raise RuntimeError("The directory %s does not exist" % recipe_dir)

    version_candidate = os.path.join(d, '..', 'version.txt')
    if os.path.exists(version_candidate):
      version = open(version_candidate).read().rstrip()
      set_environment('BOB_PACKAGE_VERSION', version)

    # pre-renders the recipe - figures out the destination
    metadata = get_rendered_metadata(d, conda_config)

    # checks if we should actually build this recipe
    if should_skip_build(metadata):
      logger.info('Skipping UNSUPPORTED build of %s for %s', recipe_dir, arch)
      continue

    rendered_recipe = get_parsed_recipe(metadata)
    path = get_output_path(metadata, conda_config)

    # Get the latest build number
    build_number, existing = next_build_number(channels[0],
        os.path.basename(path))

    should_build = True

    if existing:  #other builds exist, get the latest and see if it still works

      destpath = os.path.join(condarc_options['croot'], arch,
          os.path.basename(existing[0]))
      if not os.path.exists(os.path.dirname(destpath)):
        os.makedirs(os.path.dirname(destpath))
      src = channels[0] + existing[0]
      logger.info('Downloading %s -> %s', src, destpath)
      urllib.request.urlretrieve(src, destpath)

      # conda_build may either raise an exception or return ``False`` in case
      # the build fails, depending on the reason.  This bit of code tries to
      # accomodate both code paths and decides if we should rebuild the package
      # or not
      logger.info('Testing %s', src)
      try:
        result = conda_build.api.test(destpath, config=conda_config)
        should_build = not result
      except Exception as error:
        logger.exception(error)
      except:
        logger.error('conda_build.api.test() threw an unknown exception - ' \
            'looks like bad programming, but not on our side this time...')

      if should_build:
        logger.warn('Test for %s: FAILED. Building...', src)
      else:
        logger.info('Test for %s: SUCCESS (package is up-to-date)', src)


    if should_build:  #something wrong happened, run a full build

      logger.info('Re-building %s-%s-py%s (build: %d) for %s',
          rendered_recipe['package']['name'],
          rendered_recipe['package']['version'], python.replace('.',''),
          build_number, arch)

      if not dry_run:
        # set $BOB_BUILD_NUMBER and force conda_build to reparse recipe to get it
        # right
        set_environment('BOB_BUILD_NUMBER', str(build_number))
        paths = conda_build.api.build(d, config=conda_config, notest=False)
        # if you get to this point, the package was successfully rebuilt
        # set environment to signal caller we may dispose of it
        os.environ['BDT_BUILD'] = ':'.join(paths)

    else:  #skip build, test worked
      logger.info('Skipping rebuild of %s-%s-py%s (build: %d) for %s',
          rendered_recipe['package']['name'],
          rendered_recipe['package']['version'], python.replace('.',''),
          build_number, arch)
