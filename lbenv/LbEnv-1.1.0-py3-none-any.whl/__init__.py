#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import os
import sys

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'unknown'


def which(name, path=None):
    """
    Locate a file in the path.
    """
    if path is None:
        path = os.environ.get('PATH', '')
    if isinstance(path, str):
        path = path.split(os.path.pathsep)
    for p in path:
        fp = os.path.join(p, name)
        if os.path.exists(fp):
            return fp
    return None


def resource_string(name):
    '''
    Helper to get data stored with the package.
    '''
    import pkg_resources
    data = pkg_resources.resource_string(__name__, os.path.join('data', name))
    # FIXME compatibility py2-py3
    if sys.version_info >= (3, ):
        data = data.decode()
    return data


def defaultPlatform():
    '''
    Return the default platform for the current host.
    '''
    from LbPlatformUtils import dirac_platform, can_run, requires

    host = dirac_platform()

    for line in resource_string('platforms.txt').splitlines():
        # remove comments and whitespaces
        platform = line.split('#', 1)[0].strip()
        if platform and can_run(host, requires(platform)):
            return platform

    raise RuntimeError('cannot find a valid platform for current host, '
                       'try lb-describe-platform')


def getProjectNames():
    '''
    Return an iterator over the known project names.
    '''
    for line in resource_string('projects.txt').splitlines():
        # remove comments and whitespaces
        project = line.split('#', 1)[0].strip()
        if project:
            yield project


def getPackageNames():
    '''
    Return an iterator over the known project names.
    '''
    for line in resource_string('packages.txt').splitlines():
        # remove comments and whitespaces
        package = line.split('#', 1)[0].strip()
        if package:
            yield package


_PROJECT_NAMES = None


def fixProjectCase(project):
    '''
    Convert a project name to its canonical case, if known, otherwise return
    the string unchanged.

    >>> fixProjectCase('gaudi')
    'Gaudi'
    >>> fixProjectCase('DAvinci')
    'DaVinci'
    >>> fixProjectCase('UnKnown')
    'UnKnown'
    '''
    global _PROJECT_NAMES
    if _PROJECT_NAMES is None:
        _PROJECT_NAMES = dict(
            (name.lower(), name) for name in getProjectNames())
    return _PROJECT_NAMES.get(project.lower(), project)
