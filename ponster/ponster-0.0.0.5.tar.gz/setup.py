#!/usr/bin/env python

#  Copyright 2019 Shad Ansari
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

import os
from setuptools import setup

# Utility function to read the README file.


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='ponster',
    version='0.0.0.5',
    description=('White box PON OLT software'),
    author='Shad Ansari',
    author_email='shad69@gmail.com',
    license='Apache License 2.0',
    keywords='openolt pon whitebox',
    url='https://github.com/shadansari',
    packages=[
        'ponster',
    ],
    scripts=['bin/ponster'],
    install_requires=[
        'futures',
        'structlog',
        'simplejson',
        'protobuf',
        'grpcio',
        'confluent_kafka',
        'click',
    ],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: System :: Networking',
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
    ],
)
