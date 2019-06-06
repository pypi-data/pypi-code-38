#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Stephen Wasilewski
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================
"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['numpy', 'matplotlib', 'clasp']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest', ]

packages = ['clipt']

data_files = []

package_data = {}


setup(
    author="Stephen Wasilewski",
    author_email='stephen@coolshadow.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7'
    ],
    description="clipt makes graphs using matplotlib from the command line",
    entry_points={"console_scripts": ['cl_plot=clipt.cl_plot:main']},
    python_requires="~=2.7",
    install_requires=requirements,
    license="Mozilla Public License 2.0 (MPL 2.0)",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='clipt',
    name='clipt',
    packages=find_packages(include=packages),
    data_files=data_files,
    package_data=package_data,
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://bitbucket.org/stephenwasilewski/clipt',
    project_urls= {'documentation': 'https://clipt.readthedocs.io/'},
    version='0.1.11',
    zip_safe=True,
)
