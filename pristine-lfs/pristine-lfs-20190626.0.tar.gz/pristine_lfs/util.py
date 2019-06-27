#############################################################################
# pristine-lfs
#
# Git and Git LFS routines
# This requires Git and git-lfs to be installed.
#
# Copyright (C) 2019 Collabora Ltd
# Andrej Shadura <andrew.shadura@collabora.co.uk>

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License version 2
# text for more details.

# You should have received a copy of the GNU General Public
# License along with this package; if not, write to the Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA
#############################################################################

from gettext import gettext as _
import logging
import sh
from sh.contrib import git
import os
from pathlib import Path

from typing import Optional, Tuple, List, IO, Any, Union

gitattributes = """*.tar.* filter=lfs diff=lfs merge=lfs -text
"""

pre_push_hook = """#!/bin/sh
git lfs pre-push "$@"
"""

class Abort(Exception):
    pass

def check_branch(name: str) -> Optional[str]:
    """
    Check a branch exists, return the hash it points at, if it does.

    None if there’s no such branch
    """
    try:
        return git('show-ref', '--heads', '--hash', '--', name)
    except sh.ErrorReturnCode:
        return None

def git_dir() -> str:
    return git('rev-parse', '--git-dir').strip('\n')

def find_remote_branches(name: str) -> List[Tuple[str, str]]:
    try:
        branches = [l.split(' ') for l in git('show-ref', '--', name).splitlines()]
        return [(b[0], b[1]) for b in branches if b[1].startswith('refs/remotes/')]
    except sh.ErrorReturnCode:
        return []

def track_remote_branch(name: str):
    remote_branches = find_remote_branches(name)
    if len(remote_branches) == 0:
        raise RuntimeError('remote branch expected but not found')
    commit, branch = remote_branches[0]
    git.branch('--track', name, branch)

def reset_index():
    git.rm('--cached', '-r', '--ignore-unmatch', '*')

def store_lfs_object(io: Any) -> str:
    return str(git.lfs.clean(io.name, _in=io))

def store_git_object(io: Any) -> str:
    return git('hash-object', '-w', '--stdin', _in=io).strip('\n')

def stage_file(filename: Union[str, bytes], io: Any):
    blob = store_git_object(io)
    if isinstance(filename, bytes):
        filename = filename.decode()
    git('update-index', '--add', '--replace', '--cacheinfo', "100644,%s,%s" % (blob, filename))

def create_commit(branch: str, message: str):
    tree = git('write-tree').strip('\n')
    if not len(tree):
        raise RuntimeError('write-tree failed')

    if check_branch(branch) is not None:
        commit = git('commit-tree', tree, '-p', branch, _in=message).strip('\n')
    else:
        commit = git('commit-tree', tree, _in=message).strip('\n')
    if not len(commit):
        raise RuntimeError('commit-tree failed')

    git('update-ref', 'refs/heads/%s' % branch, commit)

def commit_lfs_file(io: IO[bytes], branch: str):
    """
    Store the file in the LFS storage and commit it to a branch.
    """
    # make sure we include all previously committed files
    if check_branch(branch) is not None:
        git(git('ls-tree', '-r', '--full-name', branch), 'update-index', '--index-info')
    else:
        # make sure .gitattributes is present
        stage_file('.gitattributes', gitattributes)

    filename = os.path.basename(io.name)

    metadata = store_lfs_object(io)
    stage_file(filename, metadata)

    message = "pristine-lfs data for %s" % filename

    create_commit(branch, message)

    # make sure the pre-push hook has been set up
    hook_path = Path(git_dir()) / 'hooks'/ 'pre-push'
    if not hook_path.is_file():
        try:
            hook_path.parent.mkdir()
            hook_path.write_text(pre_push_hook)
            hook_path.chmod(0o755)
        except IOError as e:
            logging.warning(_('Failed to set up pre-push hook: %s') % e.strerror)

def list_lfs_files(branch: str) -> List[str]:
    return git.lfs('ls-files', '--name-only', branch).splitlines()

def parse_entry(entry: str) -> Tuple[str, ...]:
    info, name = entry.split('\t')
    mode, type, hash = info.split(' ')
    return mode, type, hash, name

def list_git_files(branch: str) -> List[Tuple[str, str]]:
    entries = [parse_entry(l) for l in git('ls-tree', '-r', '--full-name', branch).splitlines()]
    return {e[3]: e[2] for e in entries if e[1] == 'blob'}

def checkout_lfs_file(branch: str, filename: str, outdir: str = '.'):
    files = list_git_files(branch)
    if filename not in files:
        raise Abort(_('%s not found on branch %s') % (filename, branch))

    metadata = git('cat-file', 'blob', files[filename])

    with (Path(outdir) / filename).open(mode='wb') as tarball:
        git.lfs.smudge(filename, _out=tarball, _in=metadata)
