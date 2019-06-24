# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Bus project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages
import os

version = '1.2.0'


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r',
          encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(os.path.join(here, 'doc', 'MEMENTO.rst'), 'r',
          encoding='utf-8') as memento_file:
    memento = memento_file.read()

with open(
    os.path.join(here, 'doc', 'CHANGES.rst'), 'r', encoding='utf-8'
) as change:
    CHANGES = change.read()

with open(
    os.path.join(here, 'doc', 'FRONT.rst'), 'r', encoding='utf-8'
) as front:
    FRONT = front.read()

requirements = [
    'anyblok',
    'pika>=1.0.1',
    'marshmallow>=3.0.0rc5',
    'furl',
]

setup(
    name='anyblok_bus',
    version=version,
    description="Bus for anyblok",
    long_description=readme + '\n' + memento + '\n' + FRONT + '\n' + CHANGES,
    author="jssuzanne",
    author_email='jssuzanne@anybox.fr',
    url="http://docs.anyblok-bus.anyblok.org/%s" % version,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'anyblok_bus=anyblok_bus.scripts:anyblok_bus',
        ],
        'bloks': [
            'bus=anyblok_bus.bloks.bus:Bus',
        ],
        'anyblok.init': [
            'bus_config=anyblok_bus:anyblok_init_config',
        ],
        'anyblok.model.plugin': [
            'bus_consumer=anyblok_bus.consumer:BusConsumerPlugin',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='bus',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='tests',
    tests_require=requirements + ['nose'],
)
