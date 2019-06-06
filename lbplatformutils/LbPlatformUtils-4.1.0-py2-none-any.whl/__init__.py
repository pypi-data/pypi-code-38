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
Utility functions for platform detection and compatibility mapping.

Part of the code was imported from Gaudi and inspired by
* https://github.com/HEP-SF/documents/tree/master/HSF-TN/draft-2015-NAM
* https://github.com/HEP-SF/tools
'''

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'unknown'

# map reference OSs to equivalent ones
OS_ALIASES = {
    'centos7': ['sl7', 'rhel7', 'opensuse42', 'opensuse15'],
    'slc6': ['sl6', 'centos6', 'rhel6'],
    'slc5': ['sl5', 'centos5', 'rhel5'],
    'ubuntu1604': [],
    'ubuntu1610': [],
    'ubuntu1704': [],
    'ubuntu1710': [],
    'ubuntu1804': [],
    'ubuntu1810': [],
    'ubuntu1904': [],
}

# define compatibility between reference OSs:
# - the OS in the key can run binaries built for the OSs in the value list
# - compatibility is meant to be transitive (if A can run B, and B can run C,
#   then A can run C) unless the entry in the list starts with '!' (e.g.
#   {'A': ['B', '!C'], 'B': ['C']} means that A cannot run C even if B can)
OS_COMPATIBILITY = {
    'centos7': ['slc6', '!slc5'],
    'slc6': ['slc5'],
    'slc5': ['slc4'],
}


def normal_name(name, aliases, default=None):
    '''
    Return the _normalized_ name corresponding to the requested one, based on
    the aliases list.  If not found return the original name, or, if specified,
    'default'.

    >>> aliases = {'a': ['1', '2', '3'],
    ...            'b': []}
    >>> normal_name('2', aliases)
    'a'
    >>> normal_name('b', aliases)
    'b'
    >>> normal_name('c', aliases)
    'c'
    >>> normal_name('c', aliases, 'unknown')
    'unknown'
    '''
    if name in aliases:
        return name
    else:
        # not a reference platform
        for k, v in aliases.items():
            if name in v:
                return k
        # not supported nor equivalent
        return default or name


def os_id(default=None):
    '''
    Return normalized OS name.

    If specified, default is used if the OS in not in the list of valid
    aliases.
    '''
    from LbPlatformUtils.inspect import os_id as _os_id
    return normal_name(_os_id(), OS_ALIASES, default)


def host_os(minimum=False):
    '''
    Return a string identifying host architecture and os, as '<arch>-<os_id>'.

    If minimum is True, use the baseline architecture.
    '''
    from LbPlatformUtils.inspect import architecture
    return '-'.join([architecture(minimum), os_id()])


def host_binary_tag(minimum=False):
    '''
    Return host binary tag string.

    If minimum is True, use the baseline architecture.

    See https://github.com/HEP-SF/documents/tree/master/HSF-TN/draft-2015-NAM
    '''
    from LbPlatformUtils.inspect import compiler_id
    return '-'.join([host_os(minimum), compiler_id(), 'opt'])


def dirac_platform(force_os=None):
    '''
    Inspect the system to return an identifier summarizing system capabilities.

    If force_os is specified use that instead of detecting it.
    '''
    from LbPlatformUtils.inspect import architecture
    arch = architecture()
    short_id = (normal_name(force_os, OS_ALIASES)
                if force_os else os_id('unknown'))
    return '-'.join([arch, short_id])


def _promote_old_style_arch(arch):
    if '+' in arch:
        from LbPlatformUtils.architectures import (ARCH_DEFS,
                                                   get_compatible_archs)
        arch, flags = arch.split('+', 1)
        flags = set(flags.split('+'))
        flags.update(ARCH_DEFS.get(arch, []))
        # take the last compatible arch
        for arch in get_compatible_archs(flags):
            pass
    return arch


def requires(binary_tag):
    '''
    Return the minimum required platform for a binary_tag.
    '''
    arch, os_id, comp = binary_tag.split('-')[:3]
    if comp.startswith('gcc') and comp >= 'gcc6':
        arch += '+sse4_2'
    arch = _promote_old_style_arch(arch)
    return '-'.join([arch, os_id])


def _parse_platform(platf):
    '''
    Split a dirac platform in a tuple (os, microarch), where microarch is None
    if not specified.

    >>> _parse_platform('i686-slc5')
    ('i686', 'slc5')
    >>> _parse_platform('x86_64-centos7.avx2')
    ('haswell', 'centos7')
    '''
    arch, os_id = platf.split('-', 1)
    if '.' in os_id:
        os_id, micro = os_id.split('.', 1)
        arch = _promote_old_style_arch(arch + '+' + micro)
    return (arch, os_id)


def check_compatibility(a, b, compatibility_map):
    '''
    Check if 'a' is compatible with 'b' according to the compatibility map.

    The compatibility_map must be a mapping from string to list of supported
    or unsupported (when prefixed with '!') strings.
    Compatibility is transitive.

    Special cases:
      * something is always compatible with itself even if not explicitly
        declared in the map.
      * if 'a' is "any" it is always compatible with 'b'

    >>> compatibility_map = {'new': ['old', '!too_old'],
    ...                      'old': ['older', 'too_old']}
    >>> check_compatibility('new', 'old', compatibility_map)
    True
    >>> check_compatibility('new', 'older', compatibility_map)
    True
    >>> check_compatibility('new', 'too_old', compatibility_map)
    False
    >>> check_compatibility('any', 'something', compatibility_map)
    True
    >>> check_compatibility('something', 'any', compatibility_map)
    False
    '''
    if a == 'any':
        return True
    if a != b:
        allowed = compatibility_map.get(a, [])
        if '!' + b in allowed:  # explicitly disallowed
            return False
        if b not in allowed:  # not explicitly allowed, recurse
            fallback = [alt for alt in allowed if not alt.startswith('!')]
            if not any(check_compatibility(f, b, compatibility_map)
                       for f in fallback):
                return False
    return True


def can_run(current, required):
    '''
    Tell if the current platform meets the constraints of the required one.
    '''
    current_arch, current_os = _parse_platform(current)
    required_arch, required_os = _parse_platform(required)
    if 'unknown' in (current_os, required_os, current_arch, required_arch):
        return False  # we do not have enough information
    # check os
    if not check_compatibility(current_os, required_os, OS_COMPATIBILITY):
        return False
    # check arch
    from LbPlatformUtils.architectures import ARCH_DEFS
    return (current_arch == required_arch
            or ARCH_DEFS.get(current_arch, set()).issuperset(
                ARCH_DEFS.get(required_arch, set(['unknown']))))


def compatible_platforms(required):
    '''
    List the dirac platforms that match the required platform.

    >>> compatible_platforms('skylake-centos7')
    ['cannonlake-centos7', 'skylake_avx512-centos7', 'skylake-centos7']
    >>> compatible_platforms('unkown-slc6')
    []
    '''
    from LbPlatformUtils.architectures import get_compatible_archs, ARCH_DEFS
    from re import findall
    required_arch, required_os = _parse_platform(required)
    # we cannot say anything about unkown OSs or architectures
    if ('unknown' in (required_arch, required_os)
            or required_arch not in ARCH_DEFS):
        return []
    # get the list of all archs that are compatible
    archs = list(get_compatible_archs(ARCH_DEFS[required_arch]))
    # get the list of all compatible OSs
    # - first get all known OSs (those from compatibility list plus
    #   the required one)
    all_OSs = set(OS_COMPATIBILITY)
    all_OSs.add(required_os)
    all_OSs = sorted(
        all_OSs,
        key=lambda s: [int(i) for i in findall(r'\d+', s)],
        reverse=True)
    # - filter by compatibility
    os_ids = [
        os_id for os_id in all_OSs
        if check_compatibility(os_id, required_os, OS_COMPATIBILITY)
    ]
    # combinatorics
    return [
        '{0}-{1}'.format(arch, os_id) for os_id in os_ids for arch in archs
    ]


def lowest_common_requirement(configs):
    '''
    Given a collection of LHCb platform ids, return the minimum required dirac
    platform that can run all of them, returning None if it cannot be found.

    >>> print(lowest_common_requirement(['x86_64+avx2+fma-slc6-gcc7-opt',
    ...                                  'x86_64-centos7-gcc62-opt']))
    haswell-centos7
    >>> print(lowest_common_requirement(['x86_64-slc5-gcc49-opt',
    ...                                 'x86_64-centos7-gcc8-opt']))
    None
    '''
    what = None
    for c in configs:
        if what is None:
            what = compatible_platforms(requires(c))
        else:
            what = [p for p in compatible_platforms(requires(c)) if p in what]
    if what:
        return what[-1]
    else:
        return None


def host_supports_tag(host_info, binary_tag, container=None):
    '''
    Return True if the given host and binary_tag are compatible.
    '''
    if container:
        from itertools import chain
        compatible_binary_tags = chain.from_iterable(
            host_info['container_technology'].get(container).values())
    else:
        compatible_binary_tags = host_info['compatible_binary_tags']
    return binary_tag in compatible_binary_tags


def get_viable_containers(host_info, platform):
    '''
    Return a list of viable container technologies for a given host.
    '''
    viable_containers = [
        container
        for container in host_info['container_technology']
        if host_supports_tag(host_info, platform, container)
    ]
    return viable_containers
