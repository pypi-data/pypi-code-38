# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module keeps track of the version of the currently used Fastr framework.
It can check its version from mercurial or a saved file
"""
import binascii
import os
from typing import Optional, Tuple

_VERSIONFILE = os.path.join(os.path.dirname(__file__), 'versioninfo')
_FASTR_SRC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def get_base_version() -> Optional[str]:
    """
    Get the version from the top-level version file

    :return: the version
    :rtype str:
    """
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'version'), 'r') as version_file:
            return version_file.read().strip()
    except IOError:
        return None


def get_hg_info() -> Tuple[Optional[str], Optional[str]]:
    """
    Read information about the current mercurial branch and revision

    :return: tuple containing head revision and branch
    """
    # Get information about the version (polling mercurial if possible)
    dirstate = os.path.join(_FASTR_SRC_DIR, '.hg', 'dirstate')
    if os.path.isfile(dirstate):
        with open(dirstate, 'rb') as dirstate_file:
            current_hg_head = binascii.hexlify(dirstate_file.read(20)).decode('utf-8')
    else:
        return None, None

    branch = os.path.join(_FASTR_SRC_DIR, '.hg', 'branch')
    if os.path.isfile(branch):
        with open(branch, 'r') as branch_file:
            current_hg_branch = branch_file.read().strip()
    else:
        return None, None

    return current_hg_head, current_hg_branch


def get_saved_version() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Get cached version from file

    :return: tuple with version, head revision and branch
    """
    try:
        with open(_VERSIONFILE, 'r') as version_file:
            data = version_file.read().split()
            data = dict(x.split('=', 1) for x in data)

        return data['version'], data['hg_head'], data['hg_branch']
    except IOError:
        return None, None, None


def save_version(current_version: str, current_hg_head: str, current_hg_branch: str):
    """
    Cache the version information (useful for when installing)

    :param str current_version: version
    :param str current_hg_head: mercurial head revision
    :param str current_hg_branch: mercurial branch
    :return:
    """
    with open(_VERSIONFILE, 'w') as version_file:
        version_file.write('version={}\n'.format(current_version))
        version_file.write('hg_head={}\n'.format(current_hg_head))
        version_file.write('hg_branch={}\n'.format(current_hg_branch))


def clear_version():
    """
    Remove the cached version info
    """
    os.remove(_VERSIONFILE)


# Try to get version info
version = get_base_version()
hg_head, hg_branch = get_hg_info()

# Note that we imported from a mercurial repository
from_mercurial = hg_branch is not None

# Try to get missing info from saved versioninfo
if version is None or hg_head is None or hg_branch is None:
    _n_version, _n_hg_head, _n_hg_branch = get_saved_version()

    version = version or _n_version
    hg_head = hg_head or _n_hg_head
    hg_branch = hg_branch or _n_hg_branch

hg_head = hg_head or 'unknown'
hg_branch = hg_branch or 'unknown'

full_version = '{}_{}_{}'.format(version, hg_branch, hg_head[:7])
not_default_branch = hg_branch != 'default'
