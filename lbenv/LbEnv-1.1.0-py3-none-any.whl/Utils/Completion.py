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
'''
Helpers for shell completion functions.
'''
_actions = {}


def action(f):
    '''
    Decorator to flag the list of actions.
    '''
    _actions[f.__name__] = f
    return f


@action
def list_projects():
    'Print the list of known project names'
    from LbEnv import getProjectNames
    print('\n'.join(p for p in sorted(getProjectNames()) if p.upper() != p))


def _get_names(name, flavour='nightly'):
    from json import load
    from urllib.request import urlopen
    from LbEnv.Info import COUCHDB_ROOT
    return load(
        urlopen(
            (COUCHDB_ROOT + '_design/names/_view/{}?group=true').replace(
                'nightlies-nightly', 'nightlies-{}').format(flavour, name),
            timeout=10)).get('rows', [])


@action
def list_nightly_slots():
    'Print the list of nightly slot names used in the last 2 weeks'
    from datetime import date, timedelta
    since = str(date.today() - timedelta(days=14))
    rows = _get_names('slots')
    print('\n'.join(row['key'] for row in rows if row['value'] >= since))


@action
def list_platforms():
    'Print the list of all platforms (from nightlies db)'
    from datetime import date, timedelta
    since = str(date.today() - timedelta(days=14))
    platforms = set(
        row['key'] for row in _get_names('platforms') if row['value'] >= since)
    # FIXME: the list of platform in the release builds includes non released
    # ones
    platforms.update(row['key'] for row in _get_names('platforms', 'release')
                     if '-' in row['key'] and 'cern' not in row['key']
                     and '+o3' not in row['key'])
    print('\n'.join(sorted(platforms)))


@action
def list_compatible_platforms():
    'Print the list of all platforms (from nightlies db)'
    import LbPlatformUtils as lpu
    dirac_platform = lpu.dirac_platform()

    platforms = set(row['key'] for row in _get_names('platforms'))
    platforms.update(row['key'] for row in _get_names('platforms', 'release'))

    print('\n'.join(
        sorted(
            p for p in platforms
            if '-' in p and lpu.can_run(dirac_platform, lpu.requires(p)))))


def main():
    import sys
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('action', choices=_actions, help='action to call')

    args = parser.parse_args()

    sys.exit(_actions[args.action]())


if __name__ == '__main__':
    main()
