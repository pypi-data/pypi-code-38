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
import re
import logging

log = logging.getLogger(__name__)

# default version alias
DEFAULT_VERSION = 'prod'


def isValidVersion(project, version):
    '''
    Check if the specified version number is a valid (reasonable) one for the
    specified project.
    '''
    # FIXME: for the moment we accept only some simple values, but we should
    #        look for aliases too (LBCORE-938)
    from LbEnv.ProjectEnv.lookup import EXTERNAL_PROJECTS
    return (version.lower() in ('prod', 'latest', 'head', 'future')
            or re.match(r'^v\d+r\d+(p\d+)?(g\d+)?(-pre\d*)?$', version)
            or (project in ('LCG', 'LCGCMT')
                and re.match(r'^\d+([a-z]?|rc\d+)$', version))
            or (project.upper() in EXTERNAL_PROJECTS
                and re.match(r'\d+\.\d+\.\d+', version)))


def expandVersionAlias(project, version, platform):
    '''
    Given a project and a version, check if the version is an alias for an
    explicit version (e.g. latest, reco19) and return the real version or the argument.
    '''
    log.debug('resolving version %r for %s %s', version, project, platform)
    result = version
    if version.lower() == 'latest':
        from .lookup import listVersions
        for vers, _path in listVersions(project, platform):
            if vers.lower() != 'head':
                result = vers
                break
    else:
        # FIXME: for the moment there is no mechanism to store version aliases (LBCORE-938)
        pass
    log.debug('using %r', result)
    return result


def versionKey(v):
    '''
    For a version string with numbers alternated by alphanumeric separators,
    return a tuple containing the separators and the numbers.

    For example:
    >>> versionKey('1.2.3')
    (1, '.', 2, '.', 3)
    >>> versionKey('v10r0')
    ('v', 10, 'r', 0)
    >>> versionKey('1.2-a')
    (1, '.', 2, '-a')
    '''
    v = re.findall(r'[-a-zA-Z_.]+|\d+', v)
    return tuple([int(x) if x.isdigit() else x for x in v])


def LCGInfoName(platform):
    '''
    Return the name of the file containing the list of externals in an LCG
    relese.

    >>> LCGInfoName('x86_64-slc6-gcc49-opt')
    'LCG_externals_x86_64-slc6-gcc49-opt.txt'
    '''
    return 'LCG_externals_{0}.txt'.format(platform)
