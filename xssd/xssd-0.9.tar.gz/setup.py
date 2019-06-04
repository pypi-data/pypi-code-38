#!/usr/bin/env python
#
# Copyright (C) 2010-2019 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import os
import sys

from setuptools import setup
sys.path.insert(1, 'lib')

from xssd import __version__, __pkgname__

# Grab description for Pypi
with open('README.rst') as fhl:
    DESC = fhl.read()

# remove MANIFEST. distutils doesn't properly update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

setup(
    name=__pkgname__,
    version=__version__,
    description='Validating python structures based on XSD Subset rules.',
    long_description=DESC,
    author='Martin Owens',
    author_email='doctormo@gmail.com',
    platforms='linux',
    test_suite='tests',
    license='GPLv3',
    packages=['xssd', 'xssd.parse'],
    package_dir={'': 'lib'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: SunOS/Solaris',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
