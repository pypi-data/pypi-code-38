#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the metadata."""
from os import path
try:  # pip version 9
    from pip.req import parse_requirements
except ImportError:
    from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

# parse_requirements() returns generator of pip.req.InstallRequirement objects
INSTALL_REQS = parse_requirements('requirements.txt', session='hack')

setup(
    name='pacifica-metadata',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Pacifica Metadata',
    url='https://github.com/pacifica/pacifica-metadata/',
    long_description=open(path.join(
        path.abspath(path.dirname(__file__)),
        'README.md')).read(),
    long_description_content_type='text/markdown',
    author='David Brown',
    author_email='dmlb2000@gmail.com',
    packages=find_packages(),
    namespace_packages=['pacifica'],
    entry_points={
        'console_scripts': [
            'pacifica-metadata=pacifica.metadata.__main__:main',
            'pacifica-metadata-cmd=pacifica.metadata.admin_cmd:main'
        ]
    },
    install_requires=[str(ir.req) for ir in INSTALL_REQS]
)
