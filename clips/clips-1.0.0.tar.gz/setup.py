#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup
from os import path as os_path

# short/long description
short_desc = 'Parser for command-line applications'
here = os_path.abspath(os_path.dirname(__file__))
try:
    with open(os_path.join(here,'README.md'),'r',encoding='utf-8') as f:
        long_desc = '\n' + f.read()
except FileNotFoundError:
    long_desc = short_desc

setup(
    name='clips',
    version='1.0.0',
    description=short_desc,
    author='andrea capitanelli',
    author_email='andrea.capitanelli@gmail.com',
    maintainer='andrea capitanelli',
    maintainer_email='andrea.capitanelli@gmail.com',
    url='https://github.com/acapitanelli/clips',
    py_modules=['clips'],
    long_description=long_desc,
    long_description_content_type='text/markdown',
    keywords='cli parser commands arguments colors',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities'
    ],
    test_suite='tests',
)
