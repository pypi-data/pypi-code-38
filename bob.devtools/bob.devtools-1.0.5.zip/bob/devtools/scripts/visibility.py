#!/usr/bin/env python

import os
import sys

import click
import gitlab

from . import bdt
from ..release import get_gitlab_instance

from ..log import verbosity_option, get_logger, echo_normal, echo_warning
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Check the visibility of a package you can access

     $ bdt gitlab visibility bob/bob.extension


  2. Checks the visibility of all packages in a file list:

\b
     $ bdt gitlab getpath bob/bob.nightlies order.txt
     $ bdt gitlab visibility order.txt
''')
@click.argument('target')
@click.option('-g', '--group', default='bob', show_default=True,
    help='Gitlab default group name where packages are located (if not ' \
        'specified using a "/" on the package name - e.g. ' \
        '"bob/bob.extension")')
@verbosity_option()
@bdt.raise_on_error
def visibility(target, group):
    '''Reports visibility of gitlab repository

    This command checks if the named package is visible to the currently logged
    in user, and reports its visibility level ('public', 'internal',
    'private').  If the package does not exist or it is private to the current
    user, it says 'unknown' instead.
    '''

    gl = get_gitlab_instance()

    # reads package list or considers name to be a package name
    if os.path.exists(target) and os.path.isfile(target):
        logger.debug('Reading package names from file %s...', target)
        with open(target, 'rt') as f:
            packages = [k.strip() for k in f.readlines() if k.strip() and not \
                k.strip().startswith('#')]
    else:
        logger.debug('Assuming %s is a package name (file does not ' \
            'exist)...', target)
        packages = [target]

    # iterates over the packages and dumps required information
    for package in packages:

        if '/' not in package:
            package = '/'.join((group, package))

        # retrieves the gitlab package object
        try:
          use_package = gl.projects.get(package)
          logger.debug('Found gitlab project %s (id=%d)',
              use_package.attributes['path_with_namespace'], use_package.id)
          echo_normal('%s: %s' % (package,
            use_package.attributes['visibility'].lower()))
        except gitlab.GitlabGetError as e:
          logger.warn('Gitlab access error - package %s does not exist?',
              package)
          echo_warning('%s: unknown' % (package,))
