#!/usr/bin/env python
#
# Copyright 2019-present Shad Ansari
#

import os
from setuptools import setup

# Utility function to read the README file.


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='openolt',
    version='1.6.1.28',
    description=('White box PON OLT software'),
    author='Shad Ansari',
    author_email='shad69@gmail.com',
    license='Apache License 2.0',
    keywords='openolt pon whitebox',
    url='https://github.com/shadansari',
    packages=[
        'openolt',
    ],
    scripts=['bin/openolt'],
    install_requires=[
        'futures',
        'structlog',
        'simplejson',
        'protobuf',
        'grpcio',
        'confluent_kafka',
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
