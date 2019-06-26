# pylint: disable-msg=W0622
# copyright 2004-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of rql.
#
# rql is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# rql is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with rql. If not, see <http://www.gnu.org/licenses/>.
"""RQL packaging information."""

import sys
import subprocess
import os.path as osp
from distutils.core import Extension

__docformat__ = "restructuredtext en"

modname = "rql"
numversion = (0, 35, 2)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'

author = "Logilab"
author_email = "contact@logilab.fr"

description = "relationship query language (RQL) utilities"
long_desc = """A library providing the base utilities to handle RQL queries,
such as a parser, a type inferencer.
"""
web = "http://www.logilab.org/project/rql"
ftp = "ftp://ftp.logilab.org/pub/rql"

classifiers = [
    'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Database',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


include_dirs = []


def gecode_version():
    version = [3, 3, 1]
    if osp.exists('data/gecode_version.cc'):
        try:
            subprocess.check_call(['g++', '-o', 'gecode_version', 'data/gecode_version.cc'])
            p = subprocess.Popen("./gecode_version", stdout=subprocess.PIPE)
            vers = p.communicate()[0].decode('ascii')
            version = [int(c) for c in vers.strip().split('.')]
        except (EnvironmentError, subprocess.CalledProcessError):
            pass
    return version


def encode_version(a, b, c):
    return ((a << 16)+(b << 8)+c)


GECODE_VERSION = encode_version(*gecode_version())

if sys.platform != 'win32':
    ext_modules = [Extension('rql.rql_solve',
                             ['rql/gecode_solver.cpp'],
                             libraries=['gecodeint', 'gecodekernel', 'gecodesearch', ],
                             extra_compile_args=['-DGE_VERSION=%s' % GECODE_VERSION],
                             )
                   ]
else:
    ext_modules = [Extension('rql.rql_solve',
                             ['rql/gecode_solver.cpp'],
                             libraries=['GecodeInt-3-3-1-r-x86',
                                        'GecodeKernel-3-3-1-r-x86',
                                        'GecodeSearch-3-3-1-r-x86',
                                        'GecodeSupport-3-3-1-r-x86',
                                        ],
                             extra_compile_args=['/DGE_VERSION=%s' % GECODE_VERSION, '/EHsc'],
                             # extra_link_args=['-static-libgcc'],
                             )
                   ]

install_requires = [
    'logilab-common >= 0.47.0',
    'logilab-database >= 1.6.0',
    'yapps2 >= 2.2.0',  # XXX to ensure we don't use the broken pypi version
    'logilab-constraint >= 0.5.0',  # fallback if the gecode compiled module is missing
    'six >= 1.4.0',
    'setuptools',
    ]
