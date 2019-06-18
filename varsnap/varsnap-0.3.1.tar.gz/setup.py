#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path


# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(path.join(here, 'varsnap', '__version__.py')) as f:
    exec(f.read(), about)

setup(
    name='varsnap',

    version=about['__version__'],

    description='VarSnap',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://www.varsnap.com/',

    author='VarSnap',
    author_email='admin@varsnap.com',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='',

    packages=find_packages(exclude=["tests"]),

    install_requires=[
        'requests>=2.0,<3.0',
    ],

    test_suite="varsnap.tests",

    # testing requires flake8 and coverage but they're listed separately
    # because they need to wrap setup.py
    extras_require={
        'dev': [],
        'test': [],
    },
)
