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
'''
@author: Marco Clemencic <marco.clemencic@cern.ch>
'''
import os
from subprocess import check_output, CalledProcessError

ENV_SCRIPTS = [
    '/cvmfs/lhcb.cern.ch/lib/lhcb/LHCBDIRAC/lhcbdirac',
    '/cvmfs/lhcbdev.cern.ch/lib/lhcb/LHCBDIRAC/lhcbdirac'
]


class LHCbDiracEnvError(RuntimeError):
    pass


def listenv(command='true'):
    '''
    Print the environment produced by a command.

    @return list of environment variables as 'name=value'
    '''
    return [_f for _f in check_output(
            command + ' >/dev/null && /usr/bin/printenv --null',
            shell=True).split('\x00') if _f]


def envchanges(command):
    '''
    Return the changes produced in the environment by the specified command as
    a set of 'name=value' entries.
    '''
    return set(listenv(command)) - set(listenv())


def envdict(command, changes_only=True):
    '''
    Return a dictionary of environment variable changes (name: value) produced
    by a command.
    '''
    return dict(
        entry.split('=', 1)
        for entry in (envchanges if changes_only else listenv)(command))


def getLHCbDiracEnv(version):
    '''
    Return the changes to the environment required for the specified LHCbDirac
    version, as a dictionary.
    '''
    import logging
    for script in filter(os.path.isfile, ENV_SCRIPTS):
        try:
            logging.getLogger('getLHCbDiracEnv').debug('sourcing "%s %s"',
                                                       script, version)
            return envdict(' '.join(['source', script, version]))
        except CalledProcessError as err:
            logging.debug(str(err))
            pass  # ignore failures of the script (the version may be wrong)
    else:
        raise LHCbDiracEnvError()
