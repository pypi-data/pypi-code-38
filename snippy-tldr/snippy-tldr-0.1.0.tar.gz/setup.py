#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  SPDX-License-Identifier: Apache-2.0
#
#  Copyright 2019 Heikki J. Laaksonen  <laaksonen.heikki.j@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""setup: Install Snippy tool."""

import io
from setuptools import setup


with io.open('README.rst', mode='r', encoding='utf-8') as infile:
    README = infile.read()

REQUIRES = ()

EXTRAS_DEVEL = (
    'sphinx==1.8.5 ; python_version<="3.4"',
    'sphinx==2.0.1 ; python_version>"3.4"',
    'sphinx_rtd_theme==0.4.3'
)

EXTRAS_TEST = (
    'flake8==3.7.7',
    'pluggy==0.11.0',
    'pylint==1.9.4 ; python_version=="2.7.*"',
    'pylint==2.3.1 ; python_version>"2.7"',
    'pytest==4.5.0',
    'pytest-cov==2.7.1',
    'pytest-mock==1.10.4',
    'pytest-xdist==1.28.0',
    'tox==3.12.1'
)

setup(
    name='snippy-tldr',
    version='0.1.0',
    author='Heikki Laaksonen',
    author_email='laaksonen.heikki.j@gmail.com',
    license='Apache Software License 2.0',
    url='https://github.com/heilaaks/snippy-tldr',
    description='Snippy plugin to import tldr man pages.',
    long_description=README,
    long_description_content_type='text/x-rst',
    py_modules=['snippy_tldr'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=REQUIRES,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Documentation',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    extras_require={
        'devel': EXTRAS_DEVEL + EXTRAS_TEST,
        'test': EXTRAS_TEST
    },
    tests_require=EXTRAS_TEST,
    test_suite='tests',
    entry_points={
        'snippyplugin': [
            'tldr = snippy_tldr'
        ]
    }
)
