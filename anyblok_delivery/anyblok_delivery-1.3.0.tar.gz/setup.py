#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Delivery project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))
version = '1.3.0'

with open(os.path.join(here, 'README.rst'),
          'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(os.path.join(here, 'CHANGELOG.rst'),
          'r', encoding='utf-8') as changelog_file:
    changelog = changelog_file.read()

requirements = [
    'anyblok',
    'anyblok_mixins',
    'anyblok_postgres',
    'anyblok_attachment',
    'anyblok_address',
    'cryptography',
    'idna',
    'requests',
    'requests-toolbelt'
]

test_requirements = [
    # TODO: put package test requirements here
]

bloks = [
    'delivery=anyblok_delivery.bloks.delivery:DeliveryBlok',
    (
        'delivery_colissimo=anyblok_delivery.bloks.colissimo:'
        'DeliveryColissimoBlok'
    ),
],

setup(
    name='anyblok_delivery',
    version=version,
    description="Carrier delivery management",
    long_description=readme + '\n\n' + changelog,
    author="Franck Bret",
    author_email='franckbret@gmail.com',
    url='https://github.com/AnyBlok/AnyBlok-Delivery',
    packages=find_packages(),
    entry_points={
        'bloks': bloks,
        'console_scripts': [
            ('anyblok_update_labels_status=anyblok_delivery.scripts:'
             'update_labels_status'),
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='anyblok_delivery',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
