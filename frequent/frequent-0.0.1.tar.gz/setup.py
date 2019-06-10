# -*- coding: utf-8 -*-
"""
Setup file for frequent package.

Incorporates code from:
    https://github.com/sarugaku/cookiecutter-python-package

"""
#
#   Imports
#
import ast
import os

from setuptools import setup, find_packages


#
#   Configuration
#

ROOT = os.path.dirname(__file__)

PACKAGE_NAME = 'frequent'

VERSION = None

with open(os.path.join(ROOT, 'src', PACKAGE_NAME, '__version__.py')) as fin:
    for line in fin:
        if line.startswith('__version__ = '):
            VERSION = ast.literal_eval(line[len('__version__ = '):].strip())
            break

if VERSION is None:
    raise EnvironmentError('Failed to read version')

PYTHON_REQUIRES = ">=3.5"

REQUIRES = [
    'click',
]


#
#   Setup
#

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    package_dir={'': 'src'},
    packages=find_packages('src', include=['frequent', 'frequent.*']),

    include_package_data=True,
    package_data={
        '': ['*LICENSE', 'README*'],
    },

    python_requires=PYTHON_REQUIRES,
    install_requires=REQUIRES,
    extras_require={
        "test": [
            "pytest", "pytest-cov", "pytest-timeout", "pytest-xdist"
        ],
    },

    project_urls={
        'Source Code': 'https://www.github.com/douglasdaly/frequent-py',
        'Documentation': 'https://frequent-py.readthedocs.io/',
    }
)
