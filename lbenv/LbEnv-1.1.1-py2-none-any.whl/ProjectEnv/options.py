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

from LbEnv.ProjectEnv import SearchPathEntry, EnvSearchPathEntry, SearchPath


class LHCbDevPathEntry(EnvSearchPathEntry):
    def __init__(self):
        EnvSearchPathEntry.__init__(self, 'LHCBDEV')

    def __repr__(self):
        return '{0}()'.format(self.__class__.__name__)


class NightlyPathEntry(SearchPathEntry):
    def __init__(self, base, slot, day):
        self.base, self.slot, self.day = base, slot, day

    @property
    def path(self):
        return os.path.join(self.base, self.slot, self.day)

    def __str__(self):
        search_path = map(str, [self.path] + self.getNightlyExtraPath())
        return os.pathsep.join(search_path)

    def getNightlyExtraPath(self):
        extra_path = []
        path = self.path
        confSumm_file = os.path.join(path, 'confSummary.py')
        config_file = os.path.join(path, 'configuration.xml')
        if os.path.exists(
                confSumm_file):  # Try with the python digested version
            data = {'__file__': confSumm_file}
            exec open(confSumm_file).read() in data  # IGNORE:W0122
            # Get the list and convert it to strings
            extra_path = data.get('cmtProjectPathList', [])
        elif os.path.exists(config_file):  # Try with the XML configuration
            from LbEnv.ProjectEnv.compatibility import getNightlyCMTPROJECTPATH
            extra_path = getNightlyCMTPROJECTPATH(config_file, self.slot,
                                                  self.day)
        return map(SearchPathEntry, extra_path)

    def toCMake(self):
        return (
            '# Use the nightly builds search path if needed.\n'
            'if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/build.conf)\n'
            '  file(STRINGS ${CMAKE_CURRENT_SOURCE_DIR}/build.conf build_conf)\n'
            '  foreach(l ${build_conf})\n'
            '    if(l MATCHES "^ *([a-zA-Z_][a-zA-Z0-9_]*)=([^ ]*) *$$")\n'
            '      set(${CMAKE_MATCH_1} "${CMAKE_MATCH_2}")\n'
            '    endif()\n'
            '  endforeach()\n'
            'endif()\n'
            'if(NOT nightly_base)\n'
            '  set(nightly_base "$ENV{LHCBNIGHTLIES}")\n'
            'endif()\n'
            '\n'
            'if(nightly_slot)\n'
            '  if(EXISTS ${nightly_base}/${nightly_slot}/${nightly_day}/searchPath.cmake)\n'
            '    include(${nightly_base}/${nightly_slot}/${nightly_day}/searchPath.cmake)\n'
            '  endif()\n'
            '  list(INSERT CMAKE_PREFIX_PATH 0 "${nightly_base}/${nightly_slot}/${nightly_day}")\n'
            'endif()\n')

    def toCMT(self, shell='sh'):
        if shell == 'csh':
            return '''# Use the nightly builds search path if needed.
if ( -e build.conf ) then
    eval `sed -n '/^[^#]/{{s/^/set /;s/$/ ;/p}}' build.conf`
endif
if ( ! $?nightly_base ) then
    if ( $?LHCBNIGHTLIES ) then
        set nightly_base = "$LHCBNIGHTLIES"
    else
        set nightly_base = ""
    endif
endif

if ( $?nightly_slot && $?nightly_day ) then
    if ( $?CMTPROJECTPATH ) then
        set SAVED_CMTPROJECTPATH = ":$CMTPROJECTPATH"
    else
        set SAVED_CMTPROJECTPATH = ""
    endif
    if ( -e ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.csh ) then
        source ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.csh
    else
        setenv CMTPROJECTPATH "${nightly_base}/${nightly_slot}/${nightly_day}"
    endif
    # This a temporary work around because setupSearchPath.csh overrides CMTPROJECTPATH
    # instead of extending it.
    setenv CMTPROJECTPATH "${CMTPROJECTPATH}${SAVED_CMTPROJECTPATH}"
endif
'''
        return '''# Use the nightly builds search path if needed.
if [ -e ./build.conf ] ; then
    . ./build.conf
fi
if [ -z "$nightly_base" ] ; then
    nightly_base="$LHCBNIGHTLIES"
fi

if [ -e ${nightly_base}/${nightly_slot}/${nightly_day} ] ; then
    if [ -e ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.sh ] ; then
        SAVED_CMTPROJECTPATH="${CMTPROJECTPATH:+:$CMTPROJECTPATH}"
        . ${nightly_base}/${nightly_slot}/${nightly_day}/setupSearchPath.sh
        # This a temporary work around because setupSearchPath.sh overrides CMTPROJECTPATH
        # instead of extending it.
        export CMTPROJECTPATH="${CMTPROJECTPATH}${SAVED_CMTPROJECTPATH}"
    else
        export CMTPROJECTPATH="${nightly_base}/${nightly_slot}/${nightly_day}${CMTPROJECTPATH:+:$CMTPROJECTPATH}"
    fi
fi
'''

    def __repr__(self):
        return '{0}({1!r}, {2!r}, {3!r})'.format(
            self.__class__.__name__, self.base, self.slot, self.day)


def addSearchPath(parser):
    '''
    Common options used to extend the search path.
    '''
    if hasattr(parser, 'add_option'):
        from .options_old import addSearchPath
        return addSearchPath(parser)

    import argparse

    class LHCbDevDirAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            try:
                value = LHCbDevPathEntry()
            except ValueError:
                parser.error('--dev used, but LHCBDEV is not defined')
            namespace.dev_dirs.append(value)

    parser.add_argument(
        '--dev',
        nargs=0,
        action=LHCbDevDirAction,
        help='prepend $LHCBDEV to the search path. '
        'Note: the directories are searched in the '
        'order specified on the command line.')
    parser.add_argument(
        '--dev-dir',
        metavar='DEVDIR',
        action='append',
        type=SearchPathEntry,
        dest='dev_dirs',
        help='prepend DEVDIR to the search path. '
        'Note: the directories are searched in the '
        'order specified on the command line.',
        default=SearchPath([]))

    class NightlyBaseAction(argparse.Action):
        '''
        Action for the --nightly-base option.
        '''

        def __call__(self, parser, namespace, values, option_string=None):
            if namespace.nightly:
                raise parser.error(
                    '%s specified after --nightly' % option_string)

            if not os.path.isdir(values):
                raise parser.error('"%s" is not a directory' % values)

            namespace.nightly_bases.append(values)

    parser.add_argument(
        '--nightly-base',
        action=NightlyBaseAction,
        dest='nightly_bases',
        help='add the specified directory to the nightly builds '
        'search path (must be specified before --nightly)',
        default=[])

    class NightlySlotAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            valid_value = re.compile(
                r'^(mon|tue|wed|thu|fri|sat|sun|today|yesterday|'
                '\d{4}-\d\d-\d\d|\d+)$',
                re.IGNORECASE)

            try:
                slot, day = values.split('/', 1)
                if valid_value.match(day):
                    day = day.capitalize()
                elif day.lower() == 'latest':
                    day = 'latest'
            except ValueError:
                slot, day = values, 'Today'

            # Locate the requested slot in the know nightlies directories
            from os import environ
            nightly_bases = namespace.nightly_bases
            nightly_bases += [
                environ.get('LHCBNIGHTLIES',
                            '/cvmfs/lhcbdev.cern.ch/nightlies'),
                environ.get('LCG_nightlies_area',
                            '/cvmfs/sft-nightlies.cern.ch/lcg/nightlies')
            ]

            from LbEnv.ProjectEnv.lookup import (findNightlyDir,
                                                 InvalidNightlySlotError)
            try:
                slot_dir = findNightlyDir(slot, day, nightly_bases)

                nightly_base, slot, day = slot_dir.rsplit(os.sep, 2)
                namespace.dev_dirs.append(
                    NightlyPathEntry(nightly_base, slot, day))
                namespace.nightly = (slot, day, nightly_base)
            except InvalidNightlySlotError as err:
                # to be able to print a friendly message about local
                # installation of a nightly slot, we cannot exit while parsing
                # the arguments
                namespace.nightly = err

    parser.add_argument(
        '--nightly',
        action=NightlySlotAction,
        metavar='SLOT[/(DAY|id)]',
        help='Add the required slot of the LHCb nightly builds to the list of '
        'DEV dirs. DAY must be a 3 digit abbreviation of the weekday "Today", '
        'an ISO formatted date or an integer, the default is Today. Special '
        'settings of the CMTPROJECTPATH needed for the nightly build slot are '
        'taken into account.')

    parser.add_argument(
        '--help-nightly-local',
        action='store_true',
        help='Print instructions on how to install locally and use a nightly '
        'slot build')

    parser.add_argument(
        '--user-area',
        help='Use the specified path as User_release_area instead of '
        'the value of the environment variable.',
        default=os.environ.get('User_release_area'))

    parser.add_argument(
        '--no-user-area',
        action='store_true',
        help='Ignore the user release area when looking for projects.',
        default=False)

    class SiterootAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            from LbEnv.Bootstrap import collect_roots, search_path
            namespace.dev_dirs.extend(
                SearchPathEntry(entry)
                for entry in search_path(collect_roots(values)))

    parser.add_argument(
        '-r',
        '--siteroot',
        help='path to the installation root, used to add default search path')

    return parser


def addOutputLevel(parser):
    '''
    Add options to get more or less messages.
    '''
    if hasattr(parser, 'add_option'):
        from .options_old import addOutputLevel
        return addOutputLevel(parser)

    import logging
    parser.add_argument(
        '--verbose',
        action='store_const',
        const=logging.INFO,
        dest='log_level',
        help='print more information')
    parser.add_argument(
        '--debug',
        action='store_const',
        const=logging.DEBUG,
        dest='log_level',
        help='print debug messages')
    parser.add_argument(
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
    if hasattr(parser, 'add_option'):
        from .options_old import addPlatform
        return addPlatform(parser)

    parser.add_argument(
        '-c', '--platform', help='runtime platform. With "best", the most appropriate is chosen [default: %(default)s]',
        default=None)
    parser.add_argument(
        '--force-platform',
        action='store_true',
        help='ignore platform compatibility check',
        default=False)

    return parser


def checkPlatform(parser, platform):
    '''
    Validate platform obtained from the parser to get the right value according
    to options, environment or system.
    '''
    try:
        from LbEnv import defaultPlatform
        if not platform:
            btag = os.environ.get('BINARY_TAG')
            cconf = os.environ.get('CMTCONFIG')
            if btag and cconf and btag != cconf:
                parser.error('inconsistent BINARY_TAG and CMTCONFIG values '
                             '(%s != %s), please unset CMTCONFIG or fix '
                             'the values' % (btag, cconf))
                return None  # needed it parser.error does not call exit
            platform = btag or cconf or defaultPlatform()
        return platform
    except RuntimeError:
        parser.error('unsupported system, check the environment or use '
                     '--platform to override the check')
        return None  # needed it parser.error does not call exit


def addListing(parser):
    '''
    Add option to request the list of versions.
    '''
    if hasattr(parser, 'add_option'):
        from .options_old import addListing
        return addListing(parser)

    parser.add_argument(
        '-l',
        '--list',
        action='store_true',
        help='list the available versions of the requested '
        'project and exit',
        default=False)
    parser.add_argument(
        '--list-versions',
        action='store_true',
        dest='list',
        help='obsolete spelling of --list',
        default=False)
    parser.add_argument(
        '-L',
        '--list-platforms',
        action='store_true',
        help='list the available platforms for the requested '
        'project/version and exit',
        default=False)

    return parser
