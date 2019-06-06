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
__all__ = ('os_id', 'architecture', 'compiler_id')

import os
import re
import platform
try:
    from subprocess import check_output, STDOUT, CalledProcessError
except ImportError:  # pragma no cover
    # check_output was introduced in Python 2.7
    from subprocess import STDOUT, CalledProcessError

    def check_output(*args, **kwargs):
        '''
        Minimal packport to Python 2.6 of check_output.
        '''
        from subprocess import Popen, PIPE
        kwargs['stdout'] = PIPE
        proc = Popen(*args, **kwargs)
        out_err = proc.communicate()
        if proc.returncode:
            raise CalledProcessError(proc.returncode, args[0])
        return out_err


# FIXME: we should only list the paths and _detect_ the os_id in there
SINGULARITY_ROOTS = [
    ('/cvmfs/cernvm-prod.cern.ch/cvm4', 'sl7'),
    ('/cvmfs/cernvm-prod.cern.ch/cvm3', 'sl6'),
]


def parse_os_release(file_obj):
    '''
    Extract OS id from content of /etc/os-release.

    See https://www.freedesktop.org/software/systemd/man/os-release.html
    '''
    release = dict(
        stripped.split('=', 1) for line in file_obj
        for stripped in (line.strip(), ) if '=' in stripped)

    for key in release:  # values might be surrounded by quotes
        release[key] = release[key].strip('"').strip("'")

    name = release.get('ID', 'linux').split('-', 1)[0]
    compatible = name + release.get('ID_LIKE', '')
    if 'rhel' in compatible or 'suse' in compatible:
        version = release.get('VERSION_ID', '').split('.', 1)[0]
    else:
        version = (release.get('VERSION_ID',
                               'testing' if name == 'debian' else '').replace(
                                   '.', ''))
    if name == 'scientific':
        name == 'sl'  # that's the traditional name of

    return name, version


def parse_system_release(s):
    '''
    Extract OS id from content of /etc/redhat-release like files.
    '''
    name = 'unknown'
    version = ''

    m = re.match(r'(.*) release (\d+)', s)
    if m:
        fullname, version = m.groups()
        if 'CERN' in fullname:
            name = 'slc'
        elif 'Scientific Linux' in fullname:
            name = 'sl'
        elif 'CentOS' in fullname:
            name = 'centos'
        elif 'Red Hat Enterprise Linux' in fullname:
            name = 'rhel'

    return name, version


def parse_lsb_release(lines):
    '''
    Extract OS id from content of /etc/lsb-release files (in Debian derived OSs).
    '''
    name = 'unknown'
    version = ''

    for l in lines:
        if l.startswith('DISTRIB_ID='):
            name = l.strip()[11:].lower()
        elif l.startswith('DISTRIB_RELEASE='):
            version = l.strip()[16:].replace('.', '')

    return name, version


def _Linux_os():
    name = 'unknown'
    version = ''

    try:
        if os.path.exists('/etc/os-release'):
            name, version = parse_os_release(open('/etc/os-release'))

        elif os.path.exists('/etc/redhat-release'):
            name, version = parse_system_release(
                open('/etc/redhat-release').read())

        elif os.path.exists('/etc/lsb-release'):
            name, version = parse_lsb_release(open('/etc/lsb-release'))

    except IOError:  # pragma: no cover
        pass  # ignore the error when we cannot read the file

    return name + version


def _Darwin_os():
    version = platform.mac_ver()[0].split('.')
    return 'macos' + ''.join(version[:2])


def _Windows_os():
    return 'win' + platform.win32_ver()[1].split('.', 1)[0]


def _unknown_os():
    return 'unknown'


_os_id_impl = globals().get('_%s_os' % platform.system(), _unknown_os)

_force_host_os_warning_printed = False


def os_id():
    if 'force_host_os' in os.environ:
        global _force_host_os_warning_printed
        if not _force_host_os_warning_printed:
            from logging import warning
            warning('overriding host os detection (using %s)',
                    os.environ['force_host_os'])
            _force_host_os_warning_printed = True
        return os.environ['force_host_os']
    return _os_id_impl()


def architecture(minimum=False):
    '''
    Return the host CPU architecture based on the supported instructions.

    The result is the most recent known architecture matching the supported
    instructions, unless minimum is set to True, in which case we return the
    base architecture.
    '''
    from LbPlatformUtils.architectures import get_supported_archs
    from itertools import dropwhile

    flags = microarch_flags()
    if flags:
        try:
            return next(
                # if minimum is True, we pick only the last of the list
                # stopping at 'x86_64' (we ignore i686 by convention)
                dropwhile(lambda a: minimum and a != 'x86_64',
                          get_supported_archs(flags)))
        except StopIteration:  # pragma no cover
            # FIXME: it's not really possible to get here because (currently)
            #        anything can run i686 code (according to the known
            #        instruction sets)
            pass
    # no flag found or architecture unknown
    return platform.machine() or 'unknown'


def model_name():
    '''
    Return CPU model name from /proc/cpuinfo.
    '''
    if os.path.exists('/proc/cpuinfo'):
        cpuinfo = open('/proc/cpuinfo')
        for l in cpuinfo:
            if l.startswith('model name'):
                return l.split(':', 1)[1].strip()
    return 'unknown'


def microarch_flags():
    '''
    Return a set with all microarchitecture flags from /proc/cpuinfo.
    '''
    if os.path.exists('/proc/cpuinfo'):
        cpuinfo = open('/proc/cpuinfo')
        for l in cpuinfo:
            if l.startswith('flags'):
                return set(l.split(':', 1)[1].split())
    # FIXME: This should probably print a warning
    return set()


def compiler_id(cmd=os.environ.get('CC', 'cc')):
    '''
    Return id of system compiler.
    '''
    # prevent interference from localization
    env = dict(os.environ)
    env['LC_ALL'] = 'C'
    try:
        m = re.search(
            r'(gcc|clang|icc|LLVM) version (\d+)\.(\d+)',
            check_output([cmd, '-v'], stderr=STDOUT, env=env).decode('utf-8'))
        comp = 'clang' if m.group(1) == 'LLVM' else m.group(1)
        vers = m.group(2)
        if (comp == 'gcc' and int(vers) < 7) or comp == 'clang':
            vers += m.group(3)
        return comp + vers
    except (AttributeError, CalledProcessError, OSError):
        # prevent crashes if the compiler is not supported or not present
        return 'unknown'


def singularity_os_ids():
    '''
    List the platforms supported via singularity container.
    '''
    available_roots = [(path, os_id) for path, os_id in SINGULARITY_ROOTS
                       if os.path.isdir(path)]

    try:
        test_cmd = [
            'singularity', 'exec', '--bind', '/cvmfs', '--no-home',
            available_roots[0][0], 'true'
        ]
        check_output(test_cmd, stderr=STDOUT).decode()
        return available_roots
    except (CalledProcessError, OSError, IndexError):
        return []
