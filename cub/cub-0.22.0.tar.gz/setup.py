#!/usr/bin/env python

import os
import cub

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

packages = ['cub']
requires = ['requests>=0.9']

setup(
    name='cub',
    version=cub.__version__,
    description='Cub Client for Python',
    long_description=open('README.rst').read(),
    author='Denis Stebunov',
    author_email='support@praetoriandigital.com',
    url='https://github.com/praetoriandigital/cub-python',
    packages=packages,
    python_requires='>=2.7.9, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=requires,
    license=open('LICENSE').readline().strip(),
    zip_safe=False,
    test_suite="tests",
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
)

del os.environ['PYTHONDONTWRITEBYTECODE']
