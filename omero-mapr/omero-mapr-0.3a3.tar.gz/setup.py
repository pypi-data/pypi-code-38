#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 University of Dundee.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>,
#
# Version: 1.0

import os
import sys
from setuptools import setup, find_packages


def get_requirements(filename='requirements.txt'):
    with open(filename) as f:
        rv = f.read().splitlines()
    return rv


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


version = __import__('omero_mapr').get_version()

install_requires = get_requirements()

tests_require = []
if "test" in sys.argv:
    tests_require = get_requirements('requirements-test.txt')

setup(
    name="omero-mapr",
    packages=find_packages(exclude=['ez_setup']),
    version=version,
    description="MAPR is a Python plugin for OMERO.web",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3 '
        'or later (AGPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Application Frameworks',  # NOQA
        'Topic :: Text Processing :: Markup :: HTML'
    ],  # Get strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    author='The Open Microscopy Team',
    author_email='ome-devel@lists.openmicroscopy.org.uk',
    license='AGPLv3',
    url="https://github.com/ome/omero-mapr",
    download_url='https://github.com/ome/omero-mapr/tarball/%s' % version,  # NOQA
    install_requires=install_requires,
    tests_require=tests_require,
    include_package_data=True,
    zip_safe=False,
    test_suite="tests",
)
