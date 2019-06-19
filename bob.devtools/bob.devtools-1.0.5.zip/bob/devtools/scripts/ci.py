#!/usr/bin/env python

import os
import re
import glob
import shutil

import yaml
import click
import pkg_resources
from click_plugins import with_plugins

from . import bdt
from ..constants import SERVER, CONDA_BUILD_CONFIG, CONDA_RECIPE_APPEND, \
    WEBDAV_PATHS, BASE_CONDARC
from ..deploy import deploy_conda_package, deploy_documentation
from ..ci import read_packages, comment_cleanup, uniq

from ..log import verbosity_option, get_logger, echo_normal
logger = get_logger(__name__)


@with_plugins(pkg_resources.iter_entry_points('bdt.ci.cli'))
@click.group(cls=bdt.AliasedGroup)
def ci():
  """Commands for building packages and handling CI activities

  Commands defined here are supposed to run on our CI, where a number of
  variables that define their behavior is correctly defined.  Do **NOT**
  attempt to run these commands in your own installation.  Unexpected errors
  may occur.
  """
  pass


@ci.command(epilog='''
Examples:

  1. Deploys base build artifacts (dependencies) to the appropriate channels:

     $ bdt ci base-deploy -vv

''')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
def base_deploy(dry_run):
    """Deploys dependencies not available at the defaults channel

    Deployment happens to our public channel directly, as these are
    dependencies are required for proper bob/beat package runtime environments.
    """

    if dry_run:
        logger.warn('!!!! DRY RUN MODE !!!!')
        logger.warn('Nothing is being deployed to server')

    package = os.environ['CI_PROJECT_PATH']
    group, name = package.split('/')

    # deploys all conda package artefacts currently available (erases them
    # afterwards)
    for arch in ('linux-64', 'osx-64', 'noarch'):
      # finds conda dependencies and uploads what we can find
      package_path = os.path.join(os.environ['CONDA_ROOT'], 'conda-bld', arch,
          '*.tar.bz2')
      deploy_packages = glob.glob(package_path)

      for k in deploy_packages:

        if os.path.basename(k).startswith(name):
          logger.debug('Skipping deploying of %s - not a base package', k)
          continue

        deploy_conda_package(k, arch=arch, stable=True, public=True,
            username=os.environ['DOCUSER'], password=os.environ['DOCPASS'],
            overwrite=False, dry_run=dry_run)


@ci.command(epilog='''
Examples:

  1. Deploys current build artifacts to the appropriate channels:

     $ bdt ci deploy -vv


  2. Deploys stable release from non-master branch (e.g. you're releasing a patch release for an older version of a package):

     $ bdt ci deploy -vv --no-latest

''')
@click.option('-n', '--latest/--no-latest', default=True,
    help='If set (the default), for stable builds, deploy documentation ' \
        'to both "stable" and "master" branches, besides "<branch>" and ' \
        '"<tag>" - otherwise, only deploys documentation to "<branch>" ' \
        'and "<tag>".  This option is useful if you are publishing ' \
        'corrections of a release from a stable branch which is **NOT** ' \
        'the master branch, so you would not like to overwrite ' \
        'documentation deployments for "stable" and "master"')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
def deploy(latest, dry_run):
    """Deploys build artifacts (conda packages and sphinx documentation)

    Deployment happens at the "right" locations - conda packages which do not
    represent stable releases are deployed to our conda "beta" channel, while
    stable packages to our root channel.  Sphinx documentation from unstable
    builds (typically the master branch) is deployed to the documentation
    server in a subdirectory named after the current branch name, while stable
    documentation is deployed to a special subdirectory named "stable" and to
    the respective tag name.
    """

    if dry_run:
        logger.warn('!!!! DRY RUN MODE !!!!')
        logger.warn('Nothing is being deployed to server')

    package = os.environ['CI_PROJECT_PATH']
    group, name = package.split('/')

    # determine if building branch or tag, and project visibility
    stable = ('CI_COMMIT_TAG' in os.environ)
    public = (os.environ['CI_PROJECT_VISIBILITY'] == 'public')

    # deploys all conda package artefacts currently available (erases them
    # afterwards)
    for arch in ('linux-64', 'osx-64', 'noarch'):
      # finds conda packages and uploads what we can find
      package_path = os.path.join(os.environ['CONDA_ROOT'], 'conda-bld', arch,
          name + '*.tar.bz2')
      deploy_packages = glob.glob(package_path)
      for k in deploy_packages:
        deploy_conda_package(k, arch=arch, stable=stable, public=public,
            username=os.environ['DOCUSER'], password=os.environ['DOCPASS'],
            overwrite=False, dry_run=dry_run)

    local_docs = os.path.join(os.environ['CI_PROJECT_DIR'], 'sphinx')
    deploy_documentation(local_docs, package, stable=stable, latest=latest,
        public=public, branch=os.environ['CI_COMMIT_REF_NAME'],
        tag=os.environ.get('CI_COMMIT_TAG'), username=os.environ['DOCUSER'],
        password=os.environ['DOCPASS'], dry_run=dry_run)


@ci.command(epilog='''
Examples:

  1. Checks the long description of setup.py (correctly parseable and will
     display nicely at PyPI).  Notice this step requires the zip python
     packages:

     $ bdt ci readme -vv dist/*.zip

''')
@click.argument('package', required=True, type=click.Path(file_okay=True,
  dir_okay=False, exists=True), nargs=-1)
@verbosity_option()
@bdt.raise_on_error
def readme(package):
    """Checks setup.py's ``long_description`` syntax

    This program checks the syntax of the contents of the ``long_description``
    field at the package's ``setup()`` function.  It verifies it will be
    correctly displayed at PyPI.
    """

    for k in package:

      logger.info('Checking python package %s', k)
      #twine check dist/*.zip

      from twine.commands.check import check
      failed = check([k])

      if failed:
        raise RuntimeError('twine check (a.k.a. readme check) %s: FAILED' % k)
      else:
        logger.info('twine check (a.k.a. readme check) %s: OK', k)

@ci.command(epilog='''
Examples:

  1. Deploys current build artifacts to the Python Package Index (PyPI):

     $ bdt ci pypi -vv dist/*.zip

''')
@click.argument('package', required=True, type=click.Path(file_okay=True,
  dir_okay=False, exists=True), nargs=-1)
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
def pypi(package, dry_run):
    """Deploys build artifacts (python packages to PyPI)

    Deployment is only allowed for packages in which the visibility is
    "public".  This check prevents publishing of private resources to the
    (public) PyPI webserver.
    """

    if dry_run:
        logger.warn('!!!! DRY RUN MODE !!!!')
        logger.warn('Nothing is being deployed to server')

    # determine project visibility
    public = (os.environ['CI_PROJECT_VISIBILITY'] == 'public')

    if not public:
      raise RuntimeError('The repository %s is not public - a package ' \
          'deriving from it therefore, CANNOT be published to PyPI. ' \
          'You must follow the relevant software disclosure procedures ' \
          'and set this repository to "public" before trying again.' % \
          os.environ['CI_PROJECT_PATH'])

    from ..constants import CACERT
    from twine.settings import Settings

    settings = Settings(
        username=os.environ['PYPIUSER'],
        password=os.environ['PYPIPASS'],
        skip_existing=True,
        cacert=CACERT,
        )

    if not dry_run:
      from twine.commands.upload import upload

      for k in package:

        logger.info('Deploying python package %s to PyPI', k)
        upload(settings, [k])
        logger.info('%s: Deployed to PyPI - OK', k)


@ci.command(epilog='''
Examples:

  1. Builds a list of non-python packages (base dependencies) defined in a text
     file:

     $ bdt ci base-build -vv order.txt


  2. Builds a list of python-dependent packages (base dependencies) defined in
     a text file, for python 3.6 and 3.7:

     $ bdt ci base-build -vv --python=3.6 --python=3.7 order.txt

''')
@click.argument('order', required=True, type=click.Path(file_okay=True,
  dir_okay=False, exists=True), nargs=1)
@click.option('-g', '--group', show_default=True, default='bob',
    help='Group of packages (gitlab namespace) this package belongs to')
@click.option('-p', '--python', multiple=True,
    help='Versions of python in the format "x.y" we should build for.  Pass ' \
        'various times this option to build for multiple python versions')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
def base_build(order, group, python, dry_run):
  """Builds base (dependence) packages

  This command builds dependence packages (packages that are not Bob/BEAT
  packages) in the CI infrastructure.  It is **not** meant to be used outside
  this context.
  """

  condarc = os.path.join(os.environ['CONDA_ROOT'], 'condarc')
  if os.path.exists(condarc):
    logger.info('Loading (this build\'s) CONDARC file from %s...', condarc)
    with open(condarc, 'rb') as f:
      condarc_options = yaml.load(f, Loader=yaml.FullLoader)

  else:  #not building on the CI? - use defaults
    from ..bootstrap import get_channels

    # get potential channel upload and other auxiliary channels
    channels = get_channels(public=True, stable=True, server=SERVER,
        intranet='True', group='bob')

    # use default and add channels
    condarc_options = yaml.load(BASE_CONDARC, Loader=yaml.FullLoader)
    channels = ['local'] + channels + ['defaults']
    logger.info('Using the following channels during build:\n  - %s',
        '\n  - '.join(channels))
    condarc_options['channels'] = channels

  # dump packages at conda_root
  condarc_options['croot'] = os.path.join(os.environ['CONDA_ROOT'],
      'conda-bld')

  # loads dirnames from order file (accepts # comments and empty lines)
  recipes = []
  with open(order, 'rt') as f:
    for line in f:
      line = line.partition('#')[0].strip()
      if line: recipes.append(line)

  import itertools
  from .. import bootstrap
  from ..build import base_build as _build

  # combine all versions of python with recipes
  if python:
    recipes = list(itertools.product(python, recipes))
  else:
    recipes = list(itertools.product([None], recipes))

  for order, (pyver, recipe) in enumerate(recipes):
    echo_normal('\n' + (80*'='))
    pytext = 'for python-%s ' % pyver if pyver is not None else ''
    echo_normal('Building "%s" %s(%d/%d)' % \
        (recipe, pytext, order+1, len(recipes)))
    echo_normal((80*'=') + '\n')
    if not os.path.exists(os.path.join(recipe, 'meta.yaml')):
      logger.info('Ignoring directory "%s" - no meta.yaml found' % recipe)
      continue

    # Use custom variants file if available on recipe-dir
    variants_file = CONDA_BUILD_CONFIG
    _candidate = os.path.join(recipe, 'conda_build_config.yaml')
    if os.path.exists(_candidate):
      variants_file = _candidate
      logger.warn('Using local conda_build_config.yaml from recipe-dir (%s)' \
          'instead of default variants file (%s)', variants_file,
          CONDA_BUILD_CONFIG)

    _build(
        bootstrap=bootstrap,
        server=SERVER,
        intranet=True,
        use_local=True,
        group=group,
        recipe_dir=recipe,
        conda_build_config=variants_file,
        python_version=pyver,
        condarc_options=condarc_options,
        )


@ci.command(epilog='''
Examples:

  1. Tests the current package

     $ bdt ci test -vv

''')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
@click.pass_context
def test(ctx, dry_run):
  """Tests packages

  This command tests packages in the CI infrastructure.  It is **not** meant
  to be used outside this context.
  """

  group = os.environ['CI_PROJECT_NAMESPACE']
  if group not in ('bob', 'beat'):
    # defaults back to bob - no other server setups are available as of now
    group = 'bob'

  # Use custom variants and append files if available on recipe-dir
  recipe_dir = os.path.join(os.path.realpath(os.curdir), 'conda')

  variants_file = CONDA_BUILD_CONFIG
  _candidate = os.path.join(recipe_dir, 'conda_build_config.yaml')
  if os.path.exists(_candidate):
    variants_file = _candidate
    logger.warn('Using local conda_build_config.yaml from recipe-dir (%s)' \
        'instead of default variants file (%s)', variants_file,
        CONDA_BUILD_CONFIG)

  append_file = CONDA_RECIPE_APPEND
  _candidate = os.path.join(recipe_dir, 'append_file.yaml')
  if os.path.exists(_candidate):
    append_file = _candidate
    logger.warn('Using local recipe_append.yaml from recipe-dir (%s)' \
        'instead of default append file (%s)', append_file,
        CONDA_RECIPE_APPEND)

  from .test import test
  ctx.invoke(test,
      package = glob.glob(os.path.join(os.environ['CONDA_ROOT'], 'conda-bld',
        '*', os.environ['CI_PROJECT_NAME'] + '*.tar.bz2')),
      condarc=None,  #custom build configuration
      config=variants_file,
      append_file=append_file,
      server=SERVER,
      group=group,
      private=(os.environ['CI_PROJECT_VISIBILITY'] != 'public'),
      stable='CI_COMMIT_TAG' in os.environ,
      use_local=False,
      dry_run=dry_run,
      ci=True,
      )


@ci.command(epilog='''
Examples:

  1. Builds the current package

     $ bdt ci build -vv

''')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
@click.pass_context
def build(ctx, dry_run):
  """Builds packages

  This command builds packages in the CI infrastructure.  It is **not** meant
  to be used outside this context.
  """

  group = os.environ['CI_PROJECT_NAMESPACE']
  if group not in ('bob', 'beat'):
    # defaults back to bob - no other server setups are available as of now
    group = 'bob'

  # Use custom variants and append files if available on recipe-dir
  recipe_dir = os.path.join(os.path.realpath(os.curdir), 'conda')

  variants_file = CONDA_BUILD_CONFIG
  _candidate = os.path.join(recipe_dir, 'conda_build_config.yaml')
  if os.path.exists(_candidate):
    variants_file = _candidate
    logger.warn('Using local conda_build_config.yaml from recipe-dir (%s)' \
        'instead of default variants file (%s)', variants_file,
        CONDA_BUILD_CONFIG)

  append_file = CONDA_RECIPE_APPEND
  _candidate = os.path.join(recipe_dir, 'append_file.yaml')
  if os.path.exists(_candidate):
    append_file = _candidate
    logger.warn('Using local recipe_append.yaml from recipe-dir (%s)' \
        'instead of default append file (%s)', append_file,
        CONDA_RECIPE_APPEND)

  from .build import build
  ctx.invoke(build,
      recipe_dir=[recipe_dir],
      python=os.environ['PYTHON_VERSION'],  #python version
      condarc=None,  #custom build configuration
      config=variants_file,
      no_test=False,
      append_file=append_file,
      server=SERVER,
      group=group,
      private=(os.environ['CI_PROJECT_VISIBILITY'] != 'public'),
      stable='CI_COMMIT_TAG' in os.environ,
      use_local=False,
      dry_run=dry_run,
      ci=True,
      )


@ci.command(epilog='''
Examples:

  1. Cleans the current build (and prints what it cleans)

     $ bdt ci clean -vv

''')
@verbosity_option()
@bdt.raise_on_error
@click.pass_context
def clean(ctx):
  """Cleans builds

  This command cleans builds in the CI infrastructure.  It is **not** meant
  to be used outside this context.
  """

  from ..build import git_clean_build
  from ..bootstrap import run_cmdline

  git_clean_build(run_cmdline, verbose=(ctx.meta['verbosity']>=3))


@ci.command(epilog='''
Examples:

  1. Runs the nightly builds following a list of packages in a file:

     $ bdt ci nightlies -vv order.txt

''')
@click.argument('order', required=True, type=click.Path(file_okay=True,
  dir_okay=False, exists=True), nargs=1)
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
@click.pass_context
def nightlies(ctx, order, dry_run):
  """Runs nightly builds

  This command can run nightly builds for packages listed on a file.

  The build or each package happens in a few phases:

  1. Package is checked out and switched to the requested branch (master if not
     set otherwise)
  2. A build string is calculated from current dependencies.  If the package
     has already been compiled, it is downloaded from the respective conda
     channel and tested.  If the test does not pass, the package is completely
     rebuilt
  3. If the rebuild is successful, the new package is uploaded to the
     respective conda channel, and the program continues with the next package

  Dependencies are searched with priority to locally built packages.  For this
  reason, the input file **must** be provided in the right dependence order.
  """

  # loads dirnames from order file (accepts # comments and empty lines)
  packages = read_packages(order)

  token = os.environ['CI_JOB_TOKEN']

  import git
  from .build import build
  from urllib.request import urlopen

  # loaded all recipes, now cycle through them implementing what is described
  # in the documentation of this function
  for n, (package, branch) in enumerate(packages):

    echo_normal('\n' + (80*'='))
    echo_normal('Building %s@%s (%d/%d)' % (package, branch, n+1,
      len(packages)))
    echo_normal((80*'=') + '\n')

    group, name = package.split('/', 1)

    clone_to = os.path.join(os.environ['CI_PROJECT_DIR'], 'src', group, name)
    dirname = os.path.dirname(clone_to)
    if not os.path.exists(dirname):
      os.makedirs(dirname)

    # clone the repo, shallow version, on the specified branch
    logger.info('Cloning "%s", branch "%s" (depth=1)...', package, branch)
    git.Repo.clone_from('https://gitlab-ci-token:%s@gitlab.idiap.ch/%s' % \
        (token, package), clone_to, branch=branch, depth=1)

    # determine package visibility
    private = urlopen('https://gitlab.idiap.ch/%s' % package).getcode() != 200
    stable = 'STABLE' in os.environ

    # Use custom variants and append files if available on recipe-dir
    recipe_dir = os.path.join(clone_to, 'conda')

    variants_file = CONDA_BUILD_CONFIG
    _candidate = os.path.join(recipe_dir, 'conda_build_config.yaml')
    if os.path.exists(_candidate):
      variants_file = _candidate
      logger.warn('Using local conda_build_config.yaml from recipe-dir (%s)' \
          'instead of default variants file (%s)', variants_file,
          CONDA_BUILD_CONFIG)

    append_file = CONDA_RECIPE_APPEND
    _candidate = os.path.join(recipe_dir, 'append_file.yaml')
    if os.path.exists(_candidate):
      append_file = _candidate
      logger.warn('Using local recipe_append.yaml from recipe-dir (%s)' \
          'instead of default append file (%s)', append_file,
          CONDA_RECIPE_APPEND)

    ctx.invoke(build,
        recipe_dir=[recipe_dir],
        python=os.environ['PYTHON_VERSION'],  #python version
        condarc=None,  #custom build configuration
        config=variants_file,
        no_test=False,
        append_file=append_file,
        server=SERVER,
        group=group,
        private=private,
        stable=stable,
        use_local=True,
        dry_run=dry_run,
        ci=True,
        )

    is_master = os.environ['CI_COMMIT_REF_NAME'] == 'master'

    # re-deploys a new conda package if it was rebuilt and it is the master
    # branch
    # n.b.: can only arrive here if dry_run was ``False`` (no need to check
    # again)
    if 'BDT_BUILD' in os.environ and is_master:
      tarball = os.environ['BDT_BUILD']
      del os.environ['BDT_BUILD']
      deploy_conda_package(tarball, arch=None, stable=stable,
          public=(not private), username=os.environ['DOCUSER'],
          password=os.environ['DOCPASS'], overwrite=False, dry_run=dry_run)

    # removes the documentation to avoid permissions issues with the following
    # projects being built
    local_docs = os.path.join(os.environ['CI_PROJECT_DIR'], 'sphinx')
    if os.path.exists(local_docs):
      logger.debug('Sphinx output was generated during test/rebuild ' \
          'of %s - Erasing...', package)
      shutil.rmtree(local_docs)


@ci.command(epilog='''
Examples:

  1. Prepares the docs for the subsequent `bdt ci build ...`:

     $ bdt ci docs -vv requirements.txt

''')
@click.argument('requirement', required=True, type=click.Path(file_okay=True,
  dir_okay=False, exists=True), nargs=1)
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
@click.pass_context
def docs(ctx, requirement, dry_run):
  """Prepares documentation build

  This command:
    1. Clones all the necessary packages necessary to build the bob/beat
       documentation
    2. Generates the `extra-intersphinx.txt` and `nitpick-exceptions.txt` file

  This command is supposed to be run **instead** of `bdt ci build...`

  """

  packages = read_packages(requirement)

  import git
  token = os.environ['CI_JOB_TOKEN']

  # loaded all recipes, now cycle through them implementing what is described
  # in the documentation of this function
  extra_intersphinx = []
  nitpick = []
  doc_path = os.path.join(os.environ['CI_PROJECT_DIR'], 'doc')

  for n, (package, branch) in enumerate(packages):

    group, name = package.split('/', 1)

    clone_to = os.path.join(doc_path, group, name)
    dirname = os.path.dirname(clone_to)
    if not os.path.exists(dirname):
      os.makedirs(dirname)

    # clone the repo, shallow version, on the specified branch
    if dry_run:
      logger.info('Cloning "%s" [%d/%d], branch "%s" (depth=1) to %s...',
          package, n+1, len(packages), branch, clone_to)
    else:
      if os.path.exists(clone_to):
         logger.info('Repo "%s" [%d/%d], already cloned at %s; ' \
             'updating branch "%s"...', package, n+1, len(packages), clone_to,
             branch)
         git.Git(clone_to).pull("origin", branch)
      else:
        logger.info('Cloning "%s" [%d/%d], branch "%s" (depth=1) to %s...',
            package, n+1, len(packages), branch, clone_to)
        git.Repo.clone_from('https://gitlab-ci-token:%s@gitlab.idiap.ch/%s' % \
                (token, package), clone_to, branch=branch, depth=1)

      # Copying the content from extra_intersphinx
      extra_intersphinx_path = os.path.join(clone_to, "doc",
          "extra-intersphinx.txt")
      if os.path.exists(extra_intersphinx_path):
        with open(extra_intersphinx_path) as f:
          extra_intersphinx += comment_cleanup(f.readlines())

      test_requirements_path = os.path.join(clone_to, "doc",
          "test-requirements.txt")
      if os.path.exists(test_requirements_path):
        with open(test_requirements_path) as f:
          extra_intersphinx += comment_cleanup(f.readliens())

      requirements_path = os.path.join(clone_to, "requirements.txt")
      if os.path.exists(requirements_path):
        with open(requirements_path) as f:
          extra_intersphinx += comment_cleanup(f.readlines())

      nitpick_path = os.path.join(clone_to, "doc", "nitpick-exceptions.txt")
      if os.path.exists(nitpick_path):
        with open(nitpick_path) as f:
          nitpick += comment_cleanup(f.readlines())

  logger.info('Generating (extra) sphinx files...')

  # Making unique lists and removing all bob/beat references
  if not dry_run:

    # extra requirements for sphinx
    group = os.environ['CI_PROJECT_NAMESPACE']
    extra_intersphinx = set([k.strip() for k in extra_intersphinx \
        if not k.strip().startswith((group, "gridtk"))])
    data = '\n'.join(uniq(sorted(extra_intersphinx)))
    logger.info('Contents of "doc/extra-intersphinx.txt":\n%s', data)
    with open(os.path.join(doc_path, 'extra-intersphinx.txt'), 'w') as f:
      f.write(data)

    # nitpick exceptions
    data = '\n'.join(uniq(sorted(nitpick)))
    logger.info('Contents of "doc/nitpick-exceptions.txt":\n%s', data)
    with open(os.path.join(doc_path, 'nitpick-exceptions.txt'), 'w') as f:
      f.write(data)

  logger.info('Building documentation...')
  ctx.invoke(build, dry_run=dry_run)
