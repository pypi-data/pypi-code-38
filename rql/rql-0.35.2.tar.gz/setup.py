#!/usr/bin/env python
# pylint: disable-msg=W0404,W0622,W0704,W0613,E0611,C0103
# copyright 2004-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Generic Setup script, takes package info from __pkginfo__.py file.
"""

from setuptools import setup, find_packages
from setuptools.command import build_ext
from io import open
import os
import os.path as osp
import sys

here = osp.abspath(osp.dirname(__file__))

pkginfo = {}
with open(osp.join(here, '__pkginfo__.py')) as f:
    exec(f.read(), pkginfo)

# Get the long description from the relevant file
with open(osp.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

kwargs = {}
if 'subpackage_of' in pkginfo:
    kwargs['namespace_packages'] = [pkginfo['subpackage_of']],

if os.environ.get('RQL_FORCE_GECODE'):
    MyBuildExt = build_ext.build_ext
else:
    class MyBuildExt(build_ext.build_ext):
        """Extend build_ext command to pass through compilation error.
        In fact, if gecode extension fail, rql will use logilab.constraint
        """

        def run(self):
            try:
                build_ext.build_ext.run(self)
            except Exception:
                import traceback
                traceback.print_exc()
                sys.stderr.write('================================\n'
                                 'The compilation of the gecode C extension failed. '
                                 'rql will use logilab.constraint which is a pure '
                                 'python implementation. '
                                 'Please note that the C extension run faster. '
                                 'So, install a compiler then install rql again with'
                                 ' the "force" option for better performance.\n'
                                 '================================\n')


setup(
    name=pkginfo.get('distname', pkginfo['modname']),
    version=pkginfo['version'],
    description=pkginfo['description'],
    long_description=long_description,
    url=pkginfo['web'],
    author=pkginfo['author'],
    author_email=pkginfo['author_email'],
    license=pkginfo['license'],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=pkginfo.get('classifiers', []),
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    install_requires=pkginfo.get('install_requires'),
    tests_require=pkginfo.get('tests_require'),
    scripts=pkginfo.get('scripts', []),
    ext_modules=pkginfo.get('ext_modules'),
    cmdclass={'build_ext': MyBuildExt},
    **kwargs
)
