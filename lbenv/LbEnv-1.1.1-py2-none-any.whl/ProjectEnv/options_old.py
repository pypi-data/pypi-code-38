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
Common functions to add common options to a OptionParser instance.
'''
__author__ = 'Marco Clemencic <marco.clemencic@cern.ch>'

import os
import re

from LbEnv.ProjectEnv import SearchPathEntry, SearchPath
from LbEnv.ProjectEnv.options import LHCbDevPathEntry, NightlyPathEntry


def addSearchPath(parser):
    '''
    Common options used to extend the search path.
    '''
    from optparse import OptionValueError

    def dev_dir_cb(option, opt_str, value, parser):
        if value is None:
            try:
                value = LHCbDevPathEntry()
            except ValueError:
                raise OptionValueError(
                    '--dev used, but LHCBDEV is not defined')
        else:
            value = SearchPathEntry(value)
        parser.values.dev_dirs.append(value)

    parser.add_option(
        '--dev',
        action='callback',
        callback=dev_dir_cb,
        help='prepend $LHCBDEV to the search path. '
        'Note: the directories are searched in the '
        'order specified on the command line.')
    parser.add_option(
        '--dev-dir',
        action='callback',
        metavar='DEVDIR',
        type='string',
        callback=dev_dir_cb,
        help='prepend DEVDIR to the search path. '
        'Note: the directories are searched in the '
        'order specified on the command line.')

    def nightly_base(option, opt_str, value, parser):
        '''
        Callback for the --nightly-base and --nightly-cvmfs options.
        '''
        if parser.values.nightly:
            raise OptionValueError('%s specified after --nightly' % option)

        if not os.path.isdir(value):
            raise OptionValueError('"%s" is not a directory' % value)

        parser.values.nightly_bases.append(value)

    parser.add_option(
        '--nightly-base',
        action='callback',
        type='string',
        callback=nightly_base,
        help='add the specified directory to the nightly builds '
        'search path (must be specified before --nightly)')

    def nightly_option(_option, opt_str, _value, _parser):
        valid_value = re.compile(
            r'^(mon|tue|wed|thu|fri|sat|sun|today|yesterday|latest|'
            '\d{4}-\d\d-\d\d|\d+)$', re.IGNORECASE)
        day = 'Today'

        parser.values.dev = True
        rargs = parser.rargs

        try:
            slot = rargs.pop(0)
        except IndexError:
            raise OptionValueError(
                '%s must be followed by the slot of the '
                'nightlies and optionally by the build id' % opt_str)

        if '/' in slot:
            slot, day = slot.split('/', 1)
            if valid_value.match(day):
                day = day.capitalize()
        elif rargs:
            match = valid_value.match(rargs[0])
            if match:
                day = rargs.pop(0).capitalize()
                import logging
                logging.warning(
                    'deprecated slot id specification: use "... '
                    '--nightly %s/%s ..." instead', slot, day)
        if day == 'Latest':  # special case
            day = 'latest'

        # Locate the requested slot in the know nightlies directories
        from os import environ
        nightly_bases = parser.values.nightly_bases
        nightly_bases += [
            environ.get('LHCBNIGHTLIES', '/cvmfs/lhcbdev.cern.ch/nightlies'),
            environ.get('LCG_nightlies_area',
                        '/cvmfs/sft-nightlies.cern.ch/lcg/nightlies')
        ]

        from LbEnv.ProjectEnv.lookup import (findNightlyDir,
                                             InvalidNightlySlotError)
        try:
            slot_dir = findNightlyDir(slot, day, nightly_bases)

            nightly_base, slot, day = slot_dir.rsplit(os.sep, 2)
            parser.values.dev_dirs.append(
                NightlyPathEntry(nightly_base, slot, day))
            parser.values.nightly = (slot, day, nightly_base)
        except InvalidNightlySlotError as err:
            # to be able to print a friendly message about local installation
            # of a nightly slot, we cannot exit while parsing the arguments
            parser.values.nightly = err

    parser.add_option(
        '--nightly',
        action='callback',
        metavar='SLOT[/DAY]',
        type='string',
        callback=nightly_option,
        nargs=0,
        help='Add the required slot of the LHCb nightly builds to the list of '
        'DEV dirs. DAY must be a 3 digit abbreviation of the weekday "Today", '
        'an ISO formatted date or an integer, the default is Today. Special '
        'settings of the CMTPROJECTPATH needed for the nightly build slot are '
        'taken into account.')

    parser.add_option(
        '--help-nightly-local',
        action='store_true',
        help='Print instructions on how to install locally and use a nightly '
        'slot build')

    parser.add_option(
        '--user-area',
        action='store',
        help='Use the specified path as User_release_area instead of '
        'the value of the environment variable.')

    parser.add_option(
        '--no-user-area',
        action='store_true',
        help='Ignore the user release area when looking for projects.')

    def siteroot_option(option, opt_str, value, parser):
        from LbEnv.Bootstrap import collect_roots, search_path
        parser.values.dev_dirs.extend(
            SearchPathEntry(entry)
            for entry in search_path(collect_roots(value)))

    parser.add_option(
        '-r', '--siteroot',
        type='string',
        action='callback',
        callback=siteroot_option,
        help='path to the installation root, used to add default search path')

    parser.set_defaults(
        dev_dirs=SearchPath([]),
        user_area=os.environ.get('User_release_area'),
        no_user_area=False,
        nightly=None,
        nightly_bases=[])

    return parser


def addOutputLevel(parser):
    '''
    Add options to get more or less messages.
    '''
    import logging
    parser.add_option(
        '--verbose',
        action='store_const',
        const=logging.INFO,
        dest='log_level',
        help='print more information')
    parser.add_option(
        '--debug',
        action='store_const',
        const=logging.DEBUG,
        dest='log_level',
        help='print debug messages')
    parser.add_option(
        '--quiet',
        action='store_const',
        const=logging.WARNING,
        dest='log_level',
        help='print only warning messages (default)')

    parser.set_defaults(log_level=logging.WARNING)

    return parser


def addPlatform(parser):
    '''
    Add option to specify a platform.
    '''

    parser.add_option(
        '-c', '--platform', help='runtime platform [default: %default]')
    parser.add_option(
        '--force-platform',
        action='store_true',
        help='ignore platform compatibility check')

    parser.set_defaults(platform=None, force_platform=False)

    return parser


def addListing(parser):
    '''
    Add option to request the list of versions.
    '''

    parser.add_option(
        '-l',
        '--list',
        action='store_true',
        help='list the available versions of the requested '
        'project and exit')
    parser.add_option(
        '--list-versions',
        action='store_true',
        dest='list',
        help='obsolete spelling of --list',
        default=False)
    parser.add_option(
        '-L',
        '--list-platforms',
        action='store_true',
        help='list the available platforms for the requested '
        'project/version and exit')

    parser.set_defaults(list=False, list_platforms=False)

    return parser
