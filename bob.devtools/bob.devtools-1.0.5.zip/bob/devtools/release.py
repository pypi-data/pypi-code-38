#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Utilities to needed to release packages'''

import os
import re
import time
import shutil
import gitlab

from .log import get_logger
logger = get_logger(__name__)

from distutils.version import StrictVersion


def download_path(package, path, output=None, ref='master'):
    '''Downloads paths from gitlab, with an optional recurse

    This method will download an archive of the repository from chosen
    reference, and then it will search insize the zip blob for the path to be
    copied into output.  It uses :py:class:`zipfile.ZipFile` to do this search.
    This method will not be very efficient for larger repository references,
    but works recursively by default.

    Args:

      package: the gitlab package object to use (should be pre-fetched)
      path: the path on the project to download
      output: where to place the path to be downloaded - if not provided, use
        the basename of ``path`` as storage point with respect to the current
        directory
      ref: the name of the git reference (branch, tag or commit hash) to use

    '''
    from io import BytesIO
    import tarfile
    import tempfile

    output = output or os.path.realpath(os.curdir)

    logger.debug('Downloading archive of "%s" from "%s"...', ref,
        package.attributes['path_with_namespace'])
    archive = package.repository_archive(ref=ref)
    logger.debug('Archive has %d bytes', len(archive))
    logger.debug('Searching for "%s" within archive...', path)

    with tempfile.TemporaryDirectory() as d:
      with tarfile.open(fileobj=BytesIO(archive), mode='r:gz') as f:
        f.extractall(path=d)

      # move stuff to "output"
      basedir = os.listdir(d)[0]
      shutil.move(os.path.join(d, basedir, path), output)


def get_gitlab_instance():
    '''Returns an instance of the gitlab object for remote operations'''

    # tries to figure if we can authenticate using a global configuration
    cfgs = ['~/.python-gitlab.cfg', '/etc/python-gitlab.cfg']
    cfgs = [os.path.expanduser(k) for k in cfgs]
    if any([os.path.exists(k) for k in cfgs]):
        gl = gitlab.Gitlab.from_config('idiap', cfgs)
    else: #ask the user for a token or use one from the current runner
        server = "https://gitlab.idiap.ch"
        token = os.environ.get('CI_JOB_TOKEN')
        if token is None:
          logger.debug('Did not find any of %s nor CI_JOB_TOKEN is defined. ' \
              'Asking for user token on the command line...', '|'.join(cfgs))
          token = input("Your %s (private) token: " % server)
        gl = gitlab.Gitlab(server, private_token=token, api_version=4)

    return gl


def _update_readme(readme, version):
    """
    Inside text of the readme, replaces parts of the links to the provided
    version. If version is not provided, replace to `stable` or `master`.

    Args:

        readme: Text of the README.rst file from a bob package
        version: Format of the version string is '#.#.#'

    Returns: New text of readme with all replaces done
    """

    # replace the badge in the readme's text with the given version
    DOC_IMAGE = re.compile(r'\-(stable|(v\d+\.\d+\.\d+([abc]\d+)?))\-')
    BRANCH_RE = re.compile(r'/(stable|master|(v\d+\.\d+\.\d+([abc]\d+)?))')

    new_readme = []
    for line in readme.splitlines():
        if BRANCH_RE.search(line) is not None:
            if "gitlab" in line:  # gitlab links
                replacement = "/v%s" % version if version is not None \
                    else "/master"
                line = BRANCH_RE.sub(replacement, line)
            if ("software/bob" in line) or \
                ("software/beat" in line):  # our doc server
                if 'master' not in line:  # don't replace 'latest' pointer
                    replacement = "/v%s" % version if version is not None \
                        else "/stable"
                    line = BRANCH_RE.sub(replacement, line)
        if DOC_IMAGE.search(line) is not None:
            replacement = '-v%s-' % version if version is not None \
                else '-stable-'
            line = DOC_IMAGE.sub(replacement, line)
        new_readme.append(line)
    return '\n'.join(new_readme) + '\n'


def get_latest_tag_name(gitpkg):
    """Find the name of the latest tag for a given package in the format '#.#.#'

    Args:
        gitpkg: gitlab package object

    Returns: The name of the latest tag in format '#.#.#'. None if no tags for
    the package were found.
    """

    # get 50 latest tags as a list
    latest_tags = gitpkg.tags.list(all=True)
    if not latest_tags:
        return None
    # create list of tags' names but ignore the first 'v' character in each name
    # also filter out non version tags
    tag_names = [tag.name[1:] for tag in latest_tags \
        if StrictVersion.version_re.match(tag.name[1:])]
    # sort them correctly according to each subversion number
    tag_names.sort(key=StrictVersion)
    # take the last one, as it is the latest tag in the sorted tags
    latest_tag_name = tag_names[-1]
    return latest_tag_name


def get_parsed_tag(gitpkg, tag):
    """
    An older tag is formatted as 'v2.1.3 (Sep 22, 2017 10:37)', from which we
    need only v2.1.3

    The latest tag is either patch, minor, major, or none
    """

    m = re.search(r"(v\d+.\d+.\d+)", tag)
    if m:
        return m.group(0)
    # tag = Version(tag)

    # if we bump the version, we need to find the latest released version for
    # this package
    if tag in ('major', 'minor', 'patch'):

        # find the correct latest tag of this package (without 'v' in front),
        # None if there are no tags yet
        latest_tag_name = get_latest_tag_name(gitpkg)

        # if there were no tags yet, assume the very first version
        if latest_tag_name is None:
            if tag == 'major':
              assume_version = 'v1.0.0'
            elif tag == 'minor':
              assume_version = 'v0.1.0'
            elif tag == 'path':
              assume_version = 'v0.0.1'
            logger.warn('Package %s does not have any tags. I\'m assuming ' \
                'version will be %s since you proposed a "%s" bump',
                gitpkg.attributes['path_with_namespace'], assume_version,
                tag)
            return assume_version

        # check that it has expected format #.#.#
        # latest_tag_name = Version(latest_tag_name)
        m = re.match(r"(\d.\d.\d)", latest_tag_name)
        if not m:
            raise ValueError('The latest tag name {0} in package {1} has ' \
                'unknown format'.format('v' + latest_tag_name,
                  gitpkg.attributes['path_with_namespace']))

        # increase the version accordingly
        major, minor, patch = latest_tag_name.split('.')

        if 'major' == tag:
            # increment the first number in 'v#.#.#' but make minor and patch
            # to be 0
            return 'v' + str(int(major) + 1) + '.0.0'

        if 'minor' == tag:
            # increment the second number in 'v#.#.#' but make patch to be 0
            return 'v' + major + '.' + str(int(minor) + 1) + '.0'

        if 'patch' == tag:
            # increment the last number in 'v#.#.#'
            return 'v' + major + '.' + minor + '.' + str(int(patch) + 1)

    if 'none' == tag:
        # we do nothing in this case
        return tag

    raise ValueError('Cannot parse changelog tag {0} of the ' \
        'package {1}'.format(tag, gitpkg.attributes['path_with_namespace']))


def update_tag_comments(gitpkg, tag_name, tag_comments_list, dry_run=False):
    """Write annotations inside the provided tag of a given package.

    Args:

        gitpkg: gitlab package object
        tag_name: The name of the tag to update
        tag_comments_list: New annotations for this tag in a form of list
        dry_run: If True, nothing will be committed or pushed to GitLab

    Returns: The gitlab object for the tag that was updated
    """

    # get tag and update its description
    logger.info(tag_name)
    tag = gitpkg.tags.get(tag_name)
    tag_comments = '\n'.join(tag_comments_list)
    logger.info('Found tag %s, updating its comments with:\n%s', tag.name,
        tag_comments)
    if not dry_run: tag.set_release_description(tag_comments)
    return tag


def update_files_with_mr(gitpkg, files_dict, message, branch, automerge,
    dry_run, user_id):
    """Update (via a commit) files of a given gitlab package, through an MR

    This function can update a file in a gitlab package, but will do this
    through a formal merge request.  You can auto-merge this request

    Args:

        gitpkg: gitlab package object
        files_dict: Dictionary of file names and their contents (as text)
        message: Commit message
        branch: The branch name to use for the merge request
        automerge: If we should set the "merge if build suceeds" flag on the
          created MR
        dry_run: If True, nothing will be pushed to gitlab
        user_id: The integer which numbers the user to attribute this MR to

    """

    data = {
        'branch': branch,
        'start_branch': 'master',
        'commit_message': message,
        'actions': []
    }

    # add files to update
    for filename in files_dict.keys():
        update_action = dict(action='update', file_path=filename)
        update_action['content'] = files_dict[filename]
        data['actions'].append(update_action)

    logger.debug("Committing changes in files (%s) to branch '%s'",
        ', '.join(files_dict.keys()), branch)
    if not dry_run:
        commit = gitpkg.commits.create(data)
        logger.info('Created commit %s at %s (branch=%s)',
            commit.short_id, gitpkg.attributes['path_with_namespace'], branch)

    logger.debug("Creating merge request %s -> master", branch)
    if not dry_run:
        mr = gitpkg.mergerequests.create({
          'source_branch': branch,
          'target_branch': 'master',
          'title': message,
          'remove_source_branch': True,
          'assignee_id': user_id,
          })
        logger.info('Created merge-request !%d (%s -> %s) at %s', mr.iid,
            branch, 'master', gitpkg.attributes['path_with_namespace'])

        if automerge:
          if '[ci skip]' in message.lower() or '[skip ci]' in message.lower():
            logger.info('Merging !%d immediately - CI was skipped', mr.iid)
            mr.merge()
          else:
            logger.info('Auto-merging !%d only if pipeline succeeds', mr.iid)
            time.sleep(0.5)  # to avoid the MR to be merged automatically - bug?
            mr.merge(merge_when_pipeline_succeeds=True)


def update_files_at_master(gitpkg, files_dict, message, dry_run):
    """Update (via a commit) files of a given gitlab package, directly on the
    master branch.

    Args:

        gitpkg: gitlab package object
        files_dict: Dictionary of file names and their contents (as text)
        message: Commit message
        dry_run: If True, nothing will be committed or pushed to GitLab

    """

    data = {
        'branch': 'master',  # v4
        'commit_message': message,
        'actions': []
    }

    # add files to update
    for filename in files_dict.keys():
        update_action = dict(action='update', file_path=filename)
        update_action['content'] = files_dict[filename]
        data['actions'].append(update_action)

    logger.debug("Committing changes in files (%s) to branch 'master'",
        ', '.join(files_dict.keys()))
    if not dry_run:
        commit = gitpkg.commits.create(data)
        logger.info('Created commit %s at %s (branch=%s)',
            commit.short_id, gitpkg.attributes['path_with_namespace'], 'master')


def get_last_pipeline(gitpkg):
    """Returns the last pipeline of the project

    Args:

        gitpkg: gitlab package object

    Returns: The gtilab object of the pipeline
    """

    # wait for 10 seconds to ensure that if a pipeline was just submitted,
    # we can retrieve it
    time.sleep(10)

    # get the last pipeline
    return gitpkg.pipelines.list(per_page=1, page=1)[0]


def just_build_package(gitpkg, dry_run=False):
    """Creates the pipeline with the latest tag and starts it

    Args:

        gitpkg: gitlab package object
        dry_run: If True, the pipeline will not be created on GitLab

    Returns:

    """

    # get the latest tag
    latest_tag_name = 'v' + get_latest_tag_name(gitpkg)

    # create the pipeline with this tag and start it
    logger.info("Creating and starting pipeline for tag %s", latest_tag_name)

    if not dry_run:
        new_pipeline = gitpkg.pipelines.create({'ref': latest_tag_name})
        return new_pipeline.id

    return None


def wait_for_pipeline_to_finish(gitpkg, pipeline_id, dry_run=False):
    """Using sleep function, wait for the latest pipeline to finish building.

    This function pauses the script until pipeline completes either
    successfully or with error.

    Args:

        gitpkg: gitlab package object
        pipeline_id: id of the pipeline for which we are waiting to finish
        dry_run: If True, outputs log message and exit. There wil be no
                 waiting.

    """

    sleep_step = 30
    max_sleep = 120 * 60  # two hours
    # pipeline = get_last_pipeline(gitpkg, before_last=before_last)

    logger.warn('Waiting for the pipeline %s of "%s" to finish',
        pipeline_id, gitpkg.attributes['path_with_namespace'])
    logger.warn('Do **NOT** interrupt!')

    if dry_run: return

    # retrieve the pipeline we are waiting for
    pipeline = gitpkg.pipelines.get(pipeline_id)

    # probe and wait for the pipeline to finish
    slept_so_far = 0

    while pipeline.status == 'running' or pipeline.status == 'pending':

        time.sleep(sleep_step)
        slept_so_far += sleep_step
        if slept_so_far > max_sleep:
            raise ValueError('I cannot wait longer than {0} seconds for '
                'pipeline {1} to finish running!'.format(max_sleep, pipeline_id))
        # probe gitlab to update the status of the pipeline
        pipeline = gitpkg.pipelines.get(pipeline_id)

    # finished running, now check if it succeeded
    if pipeline.status != 'success':
        raise ValueError('Pipeline {0} of project {1} exited with ' \
            'undesired status "{2}". Release is not possible.' \
            .format(pipeline_id, gitpkg.attributes['path_with_namespace'],
              pipeline.status))

    logger.info('Pipeline %s of package %s SUCCEEDED. Continue processing.',
        pipeline_id, gitpkg.attributes['path_with_namespace'])


def cancel_last_pipeline(gitpkg):
    """ Cancel the last started pipeline of a package

    Args:

        gitpkg: gitlab package object

    """

    pipeline = get_last_pipeline(gitpkg)
    logger.info('Cancelling the last pipeline %s of project %s', pipeline.id,
      gitpkg.attributes['path_with_namespace'])
    pipeline.cancel()


def release_package(gitpkg, tag_name, tag_comments_list, dry_run=False):
    """Release package

    The provided tag will be annotated with a given list of comments.
    README.rst and version.txt files will also be updated according to the
    release procedures.

    Args:

        gitpkg: gitlab package object
        tag_name: The name of the release tag
        tag_comments_list: New annotations for this tag in a form of list
        dry_run: If True, nothing will be committed or pushed to GitLab

    """

    # if there is nothing to release, just rebuild the package
    latest_tag = get_latest_tag_name(gitpkg)

    if tag_name == 'none' or (latest_tag and ('v' + latest_tag) == tag_name):
        logger.warn("Since the tag is 'none' or already exists, we just " \
            "re-build the last pipeline")
        return just_build_package(gitpkg, dry_run)

    # 1. Replace branch tag in Readme to new tag, change version file to new
    # version tag. Add and commit to gitlab
    version_number = tag_name[1:]  # remove 'v' in front
    readme_file = gitpkg.files.get(file_path='README.rst', ref='master')
    readme_content = readme_file.decode().decode()
    readme_content = _update_readme(readme_content, version_number)
    # commit and push changes
    update_files_at_master(gitpkg,
        {
          'README.rst': readme_content,
          'version.txt': version_number
          },
        'Increased stable version to %s' % version_number, dry_run)

    if not dry_run:
        # cancel running the pipeline triggered by the last commit
        cancel_last_pipeline(gitpkg)

    # 2. Tag package with new tag and push
    logger.info('Tagging "%s"', tag_name)
    tag_comments = '\n'.join(tag_comments_list)
    logger.debug("Updating tag comments with:\n%s", tag_comments)
    if not dry_run:
        tag = gitpkg.tags.create({'tag_name': tag_name, 'ref': 'master'})
        # update tag with comments
        tag.set_release_description(tag_comments)

    # get the pipeline that is actually running with no skips
    running_pipeline = get_last_pipeline(gitpkg)

    # 3. Replace branch tag in Readme to master, change version file to beta
    # version tag. Git add, commit, and push.
    readme_content = _update_readme(readme_content, None)
    major, minor, patch = version_number.split('.')
    version_number = '{}.{}.{}b0'.format(major, minor, int(patch)+1)
    # commit and push changes
    update_files_at_master(gitpkg, {
      'README.rst': readme_content,
      'version.txt': version_number,
      },
      'Increased latest version to %s [skip ci]' % version_number, dry_run)

    return running_pipeline.id


def parse_and_process_package_changelog(gl, gitpkg,
    package_changelog, dry_run):
    """Process the changelog of a single package

    Parse the log following specific format.  Update annotations of the
    provided older tags and release the package by following the last tag
    description.

    Args:

        gl: Gitlab API object
        gitpkg: gitlab package object
        package_changelog: the changelog corresponding to the provided package
        dry_run: If True, nothing will be committed or pushed to GitLab

    Returns: the name of the latest tag, and tag's
    comments

    """

    cur_tag = None
    cur_tag_comments = []

    # we assume that changelog is formatted as structured text
    # first line is the name of the package
    for line in package_changelog:
        if '  *' == line[:3]:  # a tag level
            # write the comments collected for the previous tag
            if cur_tag:
                update_tag_comments(gitpkg, cur_tag, cur_tag_comments, dry_run)
                cur_tag_comments = []  # reset comments

            # parse the current tag name
            cur_tag = get_parsed_tag(gitpkg, line[3:].strip())

        else:  # all other lines are assumed to be comments
            cur_tag_comments.append(line.strip())

    # return the last tag and comments for release
    return cur_tag, cur_tag_comments


def release_bob(changelog_file):
    """Process the changelog and releases the ``bob`` metapackage"""

    logger.info('Read the section "Releasing the Bob meta package" ' \
        'on the documentation')

    # get the list of bob's dependencies.
    # Get their latest tags (since bob's last release) and the tag's changelog
    saw_a_new_package = True
    latest_tag = None
    latest_pkg = None
    for line in changelog_file:
        # if saw_a_new_package:
        if line.startswith('*'):
            pkg = line[2:].strip()
            saw_a_new_package = True
            logger.info('%s == %s', latest_pkg, latest_tag)
            latest_pkg = pkg
            latest_tag = None
            continue
        if line.startswith('  *'):
            latest_tag = line.split()[1][1:]
        saw_a_new_package = False
    logger.info('%s == %s', latest_pkg, latest_tag)
    readme = open('../../bob/README.rst').read()
    readme = _update_readme(readme, bob_version)
    open('../../bob/README.rst', 'wt').write(readme)
    open('../../bob/version.txt', 'wt').write(bob_version)
