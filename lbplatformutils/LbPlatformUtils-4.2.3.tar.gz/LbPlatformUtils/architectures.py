#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# (c) Copyright 2019 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module to host definition of architecture names in terms of supported
instruction sets.
'''


def _translate_gcc_doc(s):
    '''
    Map lines describing architectures from
    https://gcc.gnu.org/onlinedocs/gcc-8.2.0/gcc/x86-Options.html#x86-Options
    to list of flags in /proc/cpuinfo

    >>> flags = _translate_gcc_doc('Intel Core 2 CPU with 64-bit extensions, '
    ... 'MMX, SSE, SSE2, SSE3 and SSSE3 instruction set support.')
    >>> sorted(flags)
    ['lm', 'mmx', 'pni', 'sse', 'sse2', 'ssse3']
    '''
    flags = set(str(s)
                .split('with', 1)[1].split('instruction set', 1)[0]
                .rstrip('.')
                .replace(',', ' ').replace('and', ' ')
                .replace('64-bit extensions', 'lm')
                .replace('.', '_')
                .lower().split())  # yapf: disable
    # Linux CPU flag names sometimes differ from the GCC wording...
    for gcc, linux in [('bmi', 'bmi1'),
                       ('adcx', 'adx'),
                       ('pclmul', 'pclmulqdq'),
                       ('rdrnd', 'rdrand'),
                       ('prefetchw', '3dnowprefetch'),
                       ('sha', 'sha_ni'),
                       ('sse3', 'pni'),
                       ('xsaves', None),  # XSAVES may not show in CPU flags
                       ]:  # yapf: disable
        if gcc in flags:
            flags.remove(gcc)
            if linux:
                flags.add(linux)
    return flags


def _parse_doc(s):
    '''
    Convert excerpt of GCC doc to an ordered dictionary of architecture names
    to set of supported instruction sets.
    '''
    from collections import OrderedDict
    archs = []
    name = desc = None
    for l in s.strip().splitlines():
        if l.startswith(u'#'):
            continue
        if l.startswith(u'‘'):
            if name:
                archs.append((name,
                              _translate_gcc_doc(desc) if desc else set()))
            name = str(l[1:-1].replace('-', '_'))
            desc = ''
        else:
            desc += l
    if name:
        archs.append((name, _translate_gcc_doc(desc) if desc else set()))
    archs.reverse()
    return OrderedDict(archs)


# Excerpt from https://gcc.gnu.org/onlinedocs/gcc-8.2.0/gcc/x86-Options.html#x86-Options
_GCC_DOC = u'''
‘i686’
#   None
‘x86-64’
    A generic CPU with 64-bit extensions.
‘core2’
    Intel Core 2 CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3 and SSSE3
    instruction set support.
‘nehalem’
    Intel Nehalem CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3,
    SSE4.1, SSE4.2 and POPCNT instruction set support.
‘westmere’
    Intel Westmere CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3,
    SSE4.1, SSE4.2, POPCNT, AES and PCLMUL instruction set support.
‘sandybridge’
    Intel Sandy Bridge CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3,
    SSE4.1, SSE4.2, POPCNT, AVX, AES and PCLMUL instruction set support.
‘ivybridge’
    Intel Ivy Bridge CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3, SSSE3,
    SSE4.1, SSE4.2, POPCNT, AVX, AES, PCLMUL, FSGSBASE, RDRND and F16C
    instruction set support.
‘haswell’
    Intel Haswell CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3,
    SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND,
    FMA, BMI, BMI2 and F16C instruction set support.
‘broadwell’
    Intel Broadwell CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3,
    SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND,
    FMA, BMI, BMI2, F16C, RDSEED, ADCX and PREFETCHW instruction set support.
‘skylake’
    Intel Skylake CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3,
    SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE, RDRND,
    FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC and
    XSAVES instruction set support.
# ‘bonnell’
#     Intel Bonnell CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3
#     and SSSE3 instruction set support.
# ‘silvermont’
#     Intel Silvermont CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2, SSE3,
#     SSSE3, SSE4.1, SSE4.2, POPCNT, AES, PCLMUL and RDRND instruction set
#     support.
# ‘knl’
#     Intel Knight’s Landing CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2,
#     SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE,
#     RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, AVX512F, AVX512PF,
#     AVX512ER and AVX512CD instruction set support.
# ‘knm’
#     Intel Knights Mill CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2,
#     SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, AVX, AVX2, AES, PCLMUL, FSGSBASE,
#     RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, AVX512F, AVX512PF,
#     AVX512ER, AVX512CD, AVX5124VNNIW, AVX5124FMAPS and AVX512VPOPCNTDQ
#     instruction set support.
‘skylake-avx512’
    Intel Skylake Server CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2,
    SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, PKU, AVX, AVX2, AES, PCLMUL, FSGSBASE,
    RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC,
    XSAVES, AVX512F, CLWB, AVX512VL, AVX512BW, AVX512DQ and AVX512CD
    instruction set support.
‘cannonlake’
    Intel Cannonlake Server CPU with 64-bit extensions, MOVBE, MMX, SSE, SSE2,
    SSE3, SSSE3, SSE4.1, SSE4.2, POPCNT, PKU, AVX, AVX2, AES, PCLMUL, FSGSBASE,
    RDRND, FMA, BMI, BMI2, F16C, RDSEED, ADCX, PREFETCHW, CLFLUSHOPT, XSAVEC,
    XSAVES, AVX512F, AVX512VL, AVX512BW, AVX512DQ, AVX512CD, AVX512VBMI,
    AVX512IFMA, SHA and UMIP instruction set support.
'''

ARCH_DEFS = _parse_doc(_GCC_DOC)
del _parse_doc
del _GCC_DOC


def _compatible_archs(flags, up):
    '''
    Helper to match compatible architectures.

    If 'up' is True, we return the included architectures, if False we return
    the including.
    '''
    flags = set(flags)
    matches = flags.issuperset if up else flags.issubset
    for name, available_flags in ARCH_DEFS.items():
        if matches(available_flags):
            yield name


def get_supported_archs(host_flags):
    '''
    Return an iterable over the list of architecture names that can be run
    on a host with the given list of microarch flags.

    >>> list(get_supported_archs(ARCH_DEFS['nehalem']))
    ['nehalem', 'core2', 'x86_64', 'i686']
    >>> list(get_supported_archs(['dummy']))
    ['i686']
    '''
    for a in _compatible_archs(host_flags, True):
        yield a


def get_compatible_archs(target_flags):
    '''
    Return an iterable over the list of architecture names that can run
    a binary compiled for with the given list of microarch flags.

    >>> list(get_compatible_archs(['avx2']))
    ['cannonlake', 'skylake_avx512', 'skylake', 'broadwell', 'haswell']
    >>> list(get_compatible_archs(['sha_ni']))
    ['cannonlake']
    '''
    for a in _compatible_archs(target_flags, False):
        yield a
