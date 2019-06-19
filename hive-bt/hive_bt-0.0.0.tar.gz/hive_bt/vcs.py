# This file is part of hive, a distributed bug tracker
# Copyright (c) 2019 by Adam Hartz <hz@mit.edu>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Helper utilities for working with version control systems.  Currently works by
invoking the binaries directly.
"""

import shutil
import subprocess


def has_git():
    return shutil.which("git") is not None


def has_hg():
    return shutil.which("hg") is not None


def _subproc_output(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.PIPE).strip().decode()
    except subprocess.CalledProcessError:
        return None


def hg_root():
    if not has_hg():
        return None
    return _subproc_output(["hg", "root"])


def git_root():
    if not has_git():
        return None
    return _subproc_output(["git", "rev-parse", "--show-toplevel"])


root_funcs = {"git": git_root, "hg": hg_root}


def get_root():
    for type_, func in root_funcs.items():
        root = func()
        if root:
            return (type_, root)
    return None


def hg_name():
    if not has_hg():
        return None
    return _subproc_output(["hg", "config", "ui.username"])


def git_name():
    if not has_git():
        return None
    name = _subproc_output(["git", "config", "--get", "user.name"])
    email = _subproc_output(["git", "config", "--get", "user.email"])
    if name is None and email is None:
        return None
    elif name is None:
        return email
    elif email is None:
        return name
    return "%s <%s>" % (name, email)


name_funcs = {"hg": hg_name, "git": git_name}


def get_repo_info():
    repo = get_root()
    if not repo:
        return None
    ident = name_funcs[repo[0]]()
    return {"type": repo[0], "root": repo[1], "name": ident}
