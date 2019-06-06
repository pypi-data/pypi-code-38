#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
Simple script to describe the platform.
'''
from __future__ import print_function

import os

BINARY_TAGS_CACHE = ('/cvmfs/lhcb.cern.ch/lib/var/lib/platforms-list.json')
BINARY_TAGS_URL = ('https://lhcb-couchdb.cern.ch/nightlies-release'
                   '/_design/names/_view/platforms?group=true')


def allBinaryTags(path=None):
    '''
    Return the list of known binary tags, either from a cache in /cvmfs or from
    the release builds database.
    '''
    import json
    try:  # pragma no cover
        from urllib.request import urlopen
        from urllib.error import URLError
    except ImportError:  # pragma no cover
        from urllib2 import urlopen, URLError

    try:
        if path is not None:
            btags = open(path)
        elif os.path.exists(BINARY_TAGS_CACHE):
            btags = open(BINARY_TAGS_CACHE)
        else:
            btags = urlopen(BINARY_TAGS_URL)
        data = btags.read()
    except (ImportError, URLError, IOError):
        import pkg_resources
        data = pkg_resources.resource_string('LbPlatformUtils',
                                             'platforms-list.json')

    if hasattr(data, 'decode'):
        data = data.decode()
    platforms_data = json.loads(data)
    # the check `if '-' in p['key']` is meant to hide obsolete platform names
    # like slc4_ia32_gcc34
    return [p['key'] for p in platforms_data.get('rows') if '-' in p['key']]


def platform_info(all_binary_tags=None):
    '''
    Return a dictionary with all details about the host platform.
    '''
    import LbPlatformUtils as lpu
    import LbPlatformUtils.inspect as inspect

    info = {}
    if all_binary_tags is None:
        all_binary_tags = allBinaryTags()

    info['LbPlatformUtils version'] = lpu.__version__

    dirac_platform = lpu.dirac_platform()

    info['dirac_platform'] = dirac_platform
    info['host_os'] = lpu.host_os()
    info['host_binary_tag'] = lpu.host_binary_tag()
    info['os_id'] = inspect.os_id()
    info['arch'] = inspect.architecture()
    info['model'] = inspect.model_name()
    info['flags'] = sorted(inspect.microarch_flags())

    info['compatible_binary_tags'] = [
        btag for btag in all_binary_tags
        if lpu.can_run(dirac_platform, lpu.requires(btag))
    ]

    info['container_technology'] = {}
    info['container_technology']['singularity'] = dict((path, [
        btag for btag in all_binary_tags
        if lpu.can_run(lpu.dirac_platform(force_os=os_id), lpu.requires(btag))
    ]) for path, os_id in inspect.singularity_os_ids())

    return info


def main(args=None):
    '''
    Simple script to describe the platform.
    '''
    try:  # pragma no cover
        from argparse import ArgumentParser
    except ImportError:  # pragma no cover
        import optparse
        optparse.OptionParser.add_argument = optparse.OptionParser.add_option
        optparse.OptionParser.parse_args_ = optparse.OptionParser.parse_args
        optparse.OptionParser.parse_args = (
            lambda self, *args, **kwargs: self.parse_args_(*args, **kwargs)[0])
        ArgumentParser = optparse.OptionParser

    from LbPlatformUtils import __version__

    parser = ArgumentParser()

    if not hasattr(parser, 'add_option'):  # pragma no cover
        # this is valid only for ArgumentParser
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(__version__))
    else:  # pragma no cover
        # this is the OptionParser
        parser.version = '%prog {0}'.format(__version__)
        parser.add_argument(
            '--version',
            action='version',
            help="show program's version number and exit")

    parser.add_argument(
        '--platforms-list',
        help='path to a file containing the list of '
        'platforms (see {0} for the format)'.format(BINARY_TAGS_URL))
    parser.add_argument(
        '--flags',
        action='store_true',
        help='also print the list of microarchitecture '
        'flags')
    parser.add_argument(
        '--raw',
        action='store_true',
        help='print a raw dictionary instead of a YAML-like format')
    parser.add_argument(
        '--no-platforms',
        action='store_true',
        help='do not print the list of compatible binary tags')
    args = parser.parse_args(args)

    if args.no_platforms and args.platforms_list:
        parser.error('incompatible options --platforms-list and '
                     '--no-platforms')

    info = platform_info(allBinaryTags(args.platforms_list))

    if args.raw:
        if not args.flags:
            del info['flags']
        from pprint import pprint
        pprint(info)
        return

    # To have a stable printout across versions of the script we hardcode
    # the order and items we want to print
    print('LbPlatformUtils version: {0}'.format(
        info['LbPlatformUtils version']))

    print('\n'.join('{0}: {1}'.format(key, info[key]) for key in [
        'dirac_platform',
        'host_os',
        'host_binary_tag',
        'os_id',
        'arch',
        'model',
    ]))

    if args.flags:
        print('flags:', *info['flags'], sep='\n  - ')

    if not args.no_platforms:  # pragma no cover
        if info['compatible_binary_tags']:
            print(
                'compatible_binary_tags:',
                *info['compatible_binary_tags'],
                sep='\n  - ')
        else:
            print('compatible_binary_tags: []')

    if info['container_technology']:  # pragma no cover
        if not args.no_platforms:
            print('container_technology:')
            for tech in info['container_technology']:
                print('  {0}:'.format(tech))
                for path, btags in info['container_technology'][tech].items():
                    if btags:
                        print(
                            '    {0}:'.format(path), *btags, sep='\n      - ')
        else:
            print(
                'container_technology:',
                *info['container_technology'],
                sep='\n  - ')
    else:  # pragma: no cover
        print('container_technology:', '[]' if args.no_platforms else '{}')


def host_binary_tag_script(args=None):
    '''
    Simple script to print the host binary tag string.
    '''
    try:  # pragma no cover
        import argparse
        parser = argparse.ArgumentParser(
            description='print default host binary tag string')
        parser.add_argument(
            '--maximum',
            action='store_false',
            help=
            'use the highest know architecture the machine can run (default)')
        parser.add_argument(
            '--minimum',
            action='store_true',
            dest='minimum',
            help='use baseline architecture rather than the highest known')
        parser.set_defaults(minimum=False)
        args = parser.parse_args(args)
    except ImportError:  # pragma no cover
        import optparse
        parser = optparse.OptionParser(
            description='print default host binary tag string')
        parser.add_option(
            '--maximum',
            action='store_false',
            help=
            'use the highest know architecture the machine can run (default)')
        parser.add_option(
            '--minimum',
            action='store_true',
            dest='minimum',
            help='use baseline architecture rather than the highest known')
        parser.set_defaults(minimum=False)
        args = parser.parse_args(args)[0]
    from LbPlatformUtils import host_binary_tag
    print(host_binary_tag(args.minimum))
