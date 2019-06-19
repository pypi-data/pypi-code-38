#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import click

from . import bdt
from ..release import release_bob, parse_and_process_package_changelog
from ..release import release_package, wait_for_pipeline_to_finish
from ..release import get_gitlab_instance

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Releases a single package:

     $ bdt gitlab release --package=bob.package.xyz changelog.md


  2. If there is a single package in the ``changelog.md`` file, the flag
     ``--package`` is not required:

     $ bdt gitlab release changelog.md


  2. Releases the whole of bob using `changelog_since_last_release.md`:

     $ bdt gitlab release bob/devtools/data/changelog_since_last_release.md


  3. In case of errors, resume the release of the whole of Bob:

     $ bdt gitlab release --resume bob/devtools/data/changelog_since_last_release.md


  4. The option `-dry-run` can be used to let the script print what it would do instead of actually doing it:

     $ bdt gitlab release --dry-run changelog_since_last_release.md
'''
)
@click.argument('changelog', type=click.File('rt', lazy=False))
@click.option('-g', '--group', default='bob', show_default=True,
    help='Group name where all packages are located (if not provided with the package)')
@click.option('-p', '--package',
    help='If the name of a package is provided, then this package will be ' \
        'found in the changelog file and the release will resume from it ' \
        '(if option ``--resume`` is set) or only this package will be ' \
        'released.  If there is only a single package in the changelog, ' \
        'then you do NOT need to set this flag')
@click.option('-r', '--resume/--no-resume', default=False,
    help='The overall release will resume from the provided package name')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
def release(changelog, group, package, resume, dry_run):
    """Tags packages on gitlab from an input CHANGELOG in markdown formatting

    By using a CHANGELOG file as an input (that can be generated with the ``bdt
    changelog`` command), this script goes through all packages in CHANGELOG
    file (in order listed), tags them correctly as per the file, and pushes
    this tag to gitlab them one by one.  Tagged releases are treated specially
    by the CI and are auto-deployed to our stable conda channels and PyPI.

    This script uses the provided CHANGELOG file to release one or more
    package.  The CHANGELOG is expected to have the following structure:

    \b
    * package name
      * tag1 name (date of the tag).
        * tag description. Each line of the tag description starts with `*`
          character.
        - commits (from earliest to latest). Each line of the commit starts
          with `-` character.
      * tag2 name (date of the tag).
        * tag description. Each line of the tag description starts with `*`
          character.
        - commits (from earliest to latest). Each line of the commit starts
          with `-` character.
      * patch
        - leftover not-tagged commits (from earliest to latest)

    This script can also be used to release a single package.

    IMPORTANT: There are some considerations that needs to be taken into
    account **before** you release a new version of a package:

    \b
    * In the changelog file:
      - write the name of this package and write (at least) the next tag value.
        For the next tag value, you can either indicate one of the special
        values: ``patch``, ``minor`` or ``major``, and the package will be then
        released with either patch, minor, or major version **bump**.
      - Alternatively, you can specify the tag value directly (using
        a ``vX.Y.Z`` format), but be careful that it is higher than the last
        release tag of this package.  Make sure that the version that you are
        trying to release is not already released.  You must follow semantic
        versioning: http://semver.org.
      - Then, under the desired new tag version of the package, please write
        down the changes that are applied to the package between the last
        released version and this version. This changes are written to
        release tags of packages in the Gitlab interface.  For an example
        look at: https://gitlab.idiap.ch/bob/bob.extension/tags
    * Make sure all the tests for the package are passing.
    * Make sure the documentation is building with the following command:
      ``sphinx-build -aEWn doc sphinx``
    * Ensure all changes are committed to the git repository and pushed.
    * Ensure the documentation badges in README.rst are pointing to:
      https://www.idiap.ch/software/bob/docs/bob/...
    * For database packages, ensure that the '.sql3' file or other metadata
      files have been generated (if any).
    * Ensure the nightlies build is green after the changes are submitted if
      the package is a part of the nightlies.
    * If your package depends on an unreleased version of another package,
      you need to release that package first.
    """

    gl = get_gitlab_instance()

    # if we are releasing 'bob' metapackage, it's a simple thing, no GitLab
    # API
    if package == 'bob':
        release_bob(changelog)
        return

    # traverse all packages in the changelog, edit older tags with updated
    # comments, tag them with a suggested version, then try to release, and
    # wait until done to proceed to the next package
    changelogs = changelog.readlines()

    # find the starts of each package's description in the changelog
    pkgs = [i for i, line in enumerate(changelogs) if line.startswith('*')]
    pkgs.append(len(changelogs)) #the end
    start_idx = 0

    if package:
        # get the index where the package first appears in the list
        start_idx = [i for i, line in enumerate(changelogs) \
            if line[1:].strip() == package]

        if not start_idx:
            logger.error('Package %s was not found in the changelog',
                package)
            return

        start_idx = pkgs.index(start_idx[0])

    # if we are in a dry-run mode, let's let it be known
    if dry_run:
        logger.warn('!!!! DRY RUN MODE !!!!')
        logger.warn('Nothing is being committed to Gitlab')

    # go through the list of packages and release them starting from the
    # start_idx
    for i in range(start_idx, len(pkgs) - 1):

        cur_package_name = changelogs[pkgs[i]][1:].strip()

        if '/' not in cur_package_name:
            cur_package_name = '/'.join((group, cur_package_name))

        # retrieves the gitlab package object
        use_package = gl.projects.get(cur_package_name)
        logger.info('Processing %s (gitlab id=%d)',
            use_package.attributes['path_with_namespace'], use_package.id)

        tag, tag_comments = parse_and_process_package_changelog(gl,
            use_package, changelogs[pkgs[i] + 1: pkgs[i + 1]], dry_run)

        # release the package with the found tag and its comments
        if use_package:
            pipeline_id = release_package(use_package, tag, tag_comments,
                dry_run)
            # now, wait for the pipeline to finish, before we can release the
            # next package
            wait_for_pipeline_to_finish(use_package, pipeline_id, dry_run)

        # if package name is provided and resume is not set, process only
        # this package
        if package == cur_package_name and not resume:
            break

    logger.info('Finished processing %s', changelog.name)
