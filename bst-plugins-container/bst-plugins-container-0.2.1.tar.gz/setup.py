#!/usr/bin/env python3
#
#  Copyright (C) 2018 Codethink Limited
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library. If not, see <http://www.gnu.org/licenses/>.
#
#  Authors:
#        Jonathan Maw <jonathan.maw@codethink.co.uk>

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    print("BuildStream requires setuptools in order to locate plugins. Install "
          "it using your package manager (usually python3-setuptools) or via "
          "pip (pip3 install setuptools).")
    sys.exit(1)

#####################################################
#     Prepare package description from README       #
#####################################################
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'README.rst')) as readme:
    long_description = readme.read()

setup(
    name='bst-plugins-container',
    version="0.2.1",
    description="A collection of BuildStream plugins that are related to containers.",
    long_description=long_description,
    long_description_content_type='text/x-rst; charset=UTF-8',
    author='BuildStream Developers',
    author_email='buildstream-list@gnome.org',
    license='LGPL',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Build Tools'
    ],
    project_urls={
        'Source': 'https://gitlab.com/BuildStream/bst-plugins-container',
        'Documentation': 'https://buildstream.gitlab.io/bst-plugins-container/',
        'Tracker': 'https://gitlab.com/BuildStream/bst-plugins-container/issues',
        'Mailing List': 'https://mail.gnome.org/mailman/listinfo/buildstream-list'
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    entry_points={
        'buildstream.plugins': [
            'docker = bst_plugins_container.sources.docker',
            'docker_image = bst_plugins_container.elements.docker_image',
        ]
    },
    extras_require={
        'test': [
            'pytest-datafiles',
            'pytest-env',
            'pytest-xdist',
            'pytest >= 3.1.0'
        ],
    },
    zip_safe=False
)  # eof setup()
