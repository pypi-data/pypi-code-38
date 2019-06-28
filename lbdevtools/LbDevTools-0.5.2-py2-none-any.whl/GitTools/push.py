from __future__ import print_function
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
__author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'

import os
import git
import logging
from collections import defaultdict
from shutil import rmtree
from subprocess import Popen, PIPE

try:
    from tempfile import TemporaryDirectory
except ImportError:
    import os as _os
    import sys as _sys
    import warnings as _warnings
    from tempfile import mkdtemp

    # FIXME: backport from Python 3.2 (see http://stackoverflow.com/a/19299884)
    class TemporaryDirectory(object):
        """Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.  For
        example:

            with TemporaryDirectory() as tmpdir:
                ...

        Upon exiting the context, the directory and everything contained
        in it are removed.
        """

        def __init__(self, suffix="", prefix="tmp", dir=None):
            self._closed = False
            self.name = None  # Handle mkdtemp raising an exception
            self.name = mkdtemp(suffix, prefix, dir)

        def __repr__(self):
            return "<{0} {1!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def cleanup(self, _warn=False):
            if self.name and not self._closed:
                try:
                    self._rmtree(self.name)
                except (TypeError, AttributeError) as ex:
                    # Issue #10188: Emit a warning on stderr
                    # if the directory could not be cleaned
                    # up due to missing globals
                    if "None" not in str(ex):
                        raise
                    print(
                        "ERROR: {0!r} while cleaning up {1!r}".format(
                            ex,
                            self,
                        ),
                        file=_sys.stderr)
                    return
                self._closed = True
                if _warn:
                    # It should be ResourceWarning, but it exists only in Python 3
                    self._warn("Implicitly cleaning up {1!r}".format(self),
                               UserWarning)

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def __del__(self):
            # Issue a ResourceWarning if implicit cleanup needed
            self.cleanup(_warn=True)

        # XXX (ncoghlan): The following code attempts to make
        # this class tolerant of the module nulling out process
        # that happens during CPython interpreter shutdown
        # Alas, it doesn't actually manage it. See issue #10188
        _listdir = staticmethod(_os.listdir)
        _path_join = staticmethod(_os.path.join)
        _isdir = staticmethod(_os.path.isdir)
        _islink = staticmethod(_os.path.islink)
        _remove = staticmethod(_os.remove)
        _rmdir = staticmethod(_os.rmdir)
        _warn = _warnings.warn

        def _rmtree(self, path):
            # Essentially a stripped down version of shutil.rmtree.  We can't
            # use globals because they may be None'ed out at shutdown.
            for name in self._listdir(path):
                fullname = self._path_join(path, name)
                try:
                    isdir = self._isdir(
                        fullname) and not self._islink(fullname)
                except OSError:
                    isdir = False
                if isdir:
                    self._rmtree(fullname)
                else:
                    try:
                        self._remove(fullname)
                    except OSError:
                        pass
            try:
                self._rmdir(path)
            except OSError:
                pass


def commits_cmp(a, b):
    '''
    History wise comparison function for commit ids.

    Used as cmp argument to a sorting function, the commits are sorted from the
    oldest to the newest.
    '''
    if a == b:
        return 0
    try:
        a.repo.iter_commits('{.hexsha}..{.hexsha}'.format(a, b)).next()
        return -1
    except StopIteration:
        return 1


def is_subdir(a, b):
    '''
    Return True if 'a' is a subdirectory of 'b' (or a == b).
    '''
    return a == b or a.startswith(b + '/')


def main():
    '''Main function of the script.'''
    from LbDevTools.GitTools.common import (add_verbosity_argument,
                                            handle_verbosity_argument,
                                            add_version_argument)
    from argparse import ArgumentParser
    parser = ArgumentParser()
    add_version_argument(parser)

    parser.add_argument('remote')
    parser.add_argument('branch')
    parser.add_argument('paths', metavar='path', nargs='*')

    add_verbosity_argument(parser)

    parser.add_argument(
        '-k',
        '--keep-temp-branch',
        action='store_true',
        dest='keep_temp',
        default=False,
        help='keep temporary branch after push instead of '
        'deleting (default=off)')

    args = parser.parse_args()
    handle_verbosity_argument(args)

    try:
        repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        logging.error('current directory is not a Git repository')
        exit(1)

    # convert paths to relative to repo workingn directory
    curdir = os.getcwd()
    args.paths = set(
        os.path.relpath(os.path.join(curdir, path), repo.working_dir)
        for path in args.paths)

    logging.info('using repository at %s', repo.working_dir)

    # find packages (directories) from the requested remote
    configfile = os.path.join(repo.working_dir, '.git-lb-checkout')
    pkgs = {}
    remotes = set()
    with git.GitConfigParser([configfile], read_only=True) as conf:
        for section in conf.sections():
            if section.startswith('lb-checkout'):
                rem, pkg = section.split('"')[1].split('.', 1)
                # collect the remotes name if we need to report errors
                remotes.add(rem)
                if rem == args.remote:
                    pkgs[pkg] = {
                        'base': conf.get_value(section, 'base'),
                        'imported': conf.get_value(section, 'imported'),
                    }

    if not pkgs:
        logging.error("No lb-checkout path found for project %s", args.remote)
        if not remotes:
            logging.warning("No lb-checkouts made")
        else:
            logging.warning("Possible projects are:")
            for m in sorted(remotes):
                logging.warning(" - {0}".format(m))
        exit(1)

    # compare the known packages to the list on the command line:
    # we take all packages that are subdirs of the specified paths
    if args.paths:
        new_pkgs = {}
        for path in args.paths:
            for pkg in pkgs:
                if is_subdir(pkg, path):
                    new_pkgs[pkg] = pkgs[pkg]
        pkgs = new_pkgs

    if not pkgs:
        logging.error('no directory selected, check your options')
        exit(1)

    logging.info('considering directories %s', pkgs.keys())

    # dictionary of dictionaries of sets
    commits_to_consider = defaultdict(lambda: defaultdict(set))
    for pkg in pkgs:
        first = True
        all_commits = list(repo.iter_commits(pkgs[pkg]['base'] + '..', pkg))
        all_commits.reverse()
        for commit in all_commits:
            commits_to_consider[commit]['packages'].add(pkg)
            if first:
                commits_to_consider[commit]['first'].add(pkg)
                first = False

    if not commits_to_consider:
        logging.error('nothing to push')
        exit(1)

    # we want to stage the commits in a temporary branch before pushing it to
    # the remote
    branches = [b.name for b in repo.branches]
    tmp_branch_name = args.branch
    cnt = 1
    while tmp_branch_name in branches:
        tmp_branch_name = '{0}-tmp{1}'.format(args.branch, cnt)
        cnt += 1
    if tmp_branch_name != args.branch:
        logging.info('using temporary branch name %s', tmp_branch_name)

    with TemporaryDirectory() as tmpdir:
        tmprepo = repo.clone(
            os.path.join(tmpdir, args.remote),
            no_checkout=True,
            reference=repo.working_dir)

        first = True
        logging.debug('sorting list of commits to consider')
        for commit in sorted(commits_to_consider, cmp=commits_cmp):
            logging.info('applying commit %s', commit.hexsha)
            commit_info = commits_to_consider[commit]
            if commit_info['first']:
                logging.debug('first commit for dirs: %s',
                              list(commit_info['first']))
            # for all packages introduced with this commit, let's take the
            # imported version first
            for pkg in commit_info['first']:
                if first:
                    # it's the very first one, we create the branch
                    tmprepo.create_head(tmp_branch_name,
                                        pkgs[pkg]['imported']).checkout()
                    first = False
                else:
                    # merging is a way to get a uniform starting point
                    tmprepo.git.merge(pkgs[pkg]['imported'], quiet=True)
                # remove original version to take into account changes in the
                # very first commit
                rmtree(os.path.join(tmprepo.working_dir, pkg))
                # checkout the local repo version of the pkg
                tmprepo.git.checkout('--quiet', commit.hexsha, '--', pkg)
            # for all packages changed (not introduced) in this commit
            pkgs_to_patch = list(commit_info['packages'] -
                                 commit_info['first'])
            if pkgs_to_patch:
                patch = tmprepo.git.format_patch(
                    '--stdout', '{0}~..{0}'.format(commit.hexsha), '--',
                    *pkgs_to_patch)
                if patch:
                    proc = Popen(['git', 'am'],
                                 stdin=PIPE,
                                 cwd=tmprepo.working_dir)
                    proc.communicate(patch)
                    if proc.returncode:
                        logging.error('failed to apply commit %s',
                                      commit.hexsha)
                        exit(proc.returncode)
        tmprepo.remote('origin').push(tmp_branch_name)

    try:
        repo.remote(args.remote).push('{0}:{1}'.format(tmp_branch_name,
                                                       args.branch))
    except Exception as err:
        logging.error("Failed to push to %s", args.remote)
        logging.error('%s: %s', type(err).__name__, err)
        if args.keep_temp:
            logging.error("Keeping temporary branch %s", tmp_branch_name)
        else:
            logging.warning("For inspection with vanilla git (e.g. --force) "
                            "use")
            logging.warning(" git lb-push --keep-temp-branch ...")
        logging.info("")
        logging.info("Possible reasons are: no push permission or branch with "
                     "the same name exists and cannot be fast-forwarded.")
    else:
        new_base = repo.head.commit.hexsha
        new_imported = getattr(repo.heads, tmp_branch_name).commit.hexsha
        with git.GitConfigParser(configfile, read_only=False) as conf:
            for pkg in pkgs:
                section = 'lb-checkout "{}.{}"'.format(args.remote, pkg)
                if not conf.has_section(section):
                    conf.add_section(section)
                conf.set(section, 'base', new_base)
                conf.set(section, 'imported', new_imported)
        repo.index.add([configfile])
        repo.index.commit('updated {} after push of {}/{}'.format(
            os.path.basename(configfile), args.remote, args.branch))
    finally:
        if args.keep_temp:
            logging.warning('Keeping branch %s. It\'s up to you to delete it.',
                            tmp_branch_name)
        else:
            repo.delete_head(tmp_branch_name, force=True)
