#!/usr/bin/env python3

"""Open Data Schema Python client"""

import io
import os

from setuptools import setup

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: MIT License
"""


def read(*paths):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    contents = io.open(fullpath, encoding='utf-8').read().strip()
    return contents


README = read('README.md')

setup(
    name='opendataschema',
    version='0.0.1',

    author='Pierre Dittgen',
    author_email='pierre.dittgen@jailbreak.paris',
    classifiers=[classifier for classifier in classifiers.split('\n') if classifier],
    description=__doc__,
    long_description=README,
    long_description_content_type="text/markdown",

    packages=['opendataschema'],

    install_requires=[
        'cachetools >= 3.1.1',
        'click >= 7.0.0',
        'jsonschema >= 3.0.1',
        'python-gitlab >= 1.8.0',
        'requests >= 2.22.0',
        'tableschema >= 1.5.1',
        'toml >= 0.10.0'
    ],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
    ],

    entry_points={
        'console_scripts': [
            'opendataschema = opendataschema.cli:cli',
        ],
    },
)
