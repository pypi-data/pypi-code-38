#!/usr/bin/env python

import os

import click

from . import bdt
from ..release import get_gitlab_instance, update_files_with_mr, \
    update_files_at_master

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Replaces the README.rst file on the package bob/bob.extension, through a direct commit to the master branch, using the contents of the local file with the same name:

     $ bdt gitlab commitfile -vv bob/bob.extension README.rst


  2. Replaces the README.rst file on the package beat/beat.core, specifying a commit message:

\b
     $ bdt gitlab commitfile -vv --message="[readme] Update [ci skip]" beat/beat.core README.rst


  3. Replaces the file conda/meta.yaml on the package bob/bob.blitz through a merge request through a new branch called "conda-changes", specifying a commit/merge-request message, using the contents of the local file new.yaml, and setting the merge-request property "merge-when-pipeline-succeeds":

\b
     $ bdt gitlab commitfile -vv bob/bob.blitz --path=conda/meta.yaml --branch=conda-changes --auto-merge new.yaml

''')
@click.argument('package')
@click.argument('file', type=click.Path(file_okay=True, dir_okay=False,
  exists=True))
@click.option('-m', '--message',
    help='Message to set for this commit',)
@click.option('-p', '--path',
    help='Which path to replace on the remote package',)
@click.option('-b', '--branch', default='master',
    help='Name of the branch to create for this commit.  If the branch ' \
        'name is not "master", then create a new branch and propose the ' \
        'merge through a proper merge-request.  Otherwise, the default ' \
        'behaviour is to commit directly to the master branch ' \
        '[default: %(default)s',)
@click.option('-a', '--auto-merge/--no-auto-merge', default=False,
    help='If set, then the created merge request will be merged when ' \
        'a potentially associated pipeline succeeds')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
def commitfile(package, message, file, path, branch, auto_merge, dry_run):
    """Changes a file on a given package, directly on master or through MR
    """

    if '/' not in package:
        raise RuntimeError('PACKAGE should be specified as "group/name"')

    gl = get_gitlab_instance()
    gl.auth()
    user_id = gl.user.attributes['id']

    # we lookup the gitlab package once
    use_package = gl.projects.get(package)
    logger.debug('Found gitlab project %s (id=%d)',
        use_package.attributes['path_with_namespace'], use_package.id)

    # if we are in a dry-run mode, let's let it be known
    if dry_run:
        logger.warn('!!!! DRY RUN MODE !!!!')
        logger.warn('Nothing is being committed to Gitlab')

    path = path or file

    # load file contents
    with open(file, 'rt') as f:
      contents = f.read()

    components = os.path.splitext(path)[0].split(os.sep)
    message = message or ("%s update" % \
        ''.join(['[%s]' % k.lower() for k in components]))

    # commit and push changes
    if branch == 'master':
      update_files_at_master(use_package, {path: contents}, message, dry_run)
    else:
      update_files_with_mr(use_package, {path: contents}, message, branch,
        auto_merge, dry_run, user_id)
