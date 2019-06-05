#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
from setuptools import setup, find_packages


def get_data_files(path):
    data_files = []
    directories = glob.glob(path)
    for directory in directories:
        files = glob.glob(directory + '*')
        data_files.append((directory, files))
    return data_files


with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'Jinja2',
    'commonmark',
    'lxml',
]

test_requirements = requirements + [
    'Jinja2',
    'commonmark',
    'lxml',
]

setup(
    name='EPCPyYes',
    version='2.0.2',
    description="EPCIS Python module for quickly developing "
                "EPCIS-enabled applications.",
    long_description=readme,
    maintainer="Rob Magee",
    author="Serial Lab",
    author_email='slab@serial-lab.com',
    url='https://gitlab.com/serial-lab/EPCPyYes',
    packages=find_packages(),
    package_dir={'EPCPyYes': 'EPCPyYes'},
    entry_points={
    },
    data_files=get_data_files('EPCPyYes/templates/epcis/') + \
               get_data_files('EPCPyYes/core/tests/schemas/'),
    include_package_data=True,
    install_requires=requirements,
    license="GNU Affero General Public License v3",
    zip_safe=False,
    keywords='EPCPyYes EPCIS GS1 RFID Serialization',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='EPCPyYes.core.tests',
    tests_require=test_requirements
)
