#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import warnings
import re
from setuptools import setup, find_packages
import sys
import os

__version__ = "0.2.4"

#ORIGINAL CLI CLIENT SETUP + old reqs
# setup(
#   name='dataspine-cli',
#   version='0.2.0-dev',
#   packages=['utils'],
#   py_modules=['cli'],
#   include_package_data=True,
#   install_requires=['click'],
#   entry_points='''
#     [console_scripts]
#     spinectl=cli:cli_commands
#   ''',
# )


# with warnings.catch_warnings():
#     requirements_path = './requirements.txt'
#     requirements_path = os.path.normpath(requirements_path)
#     requirements_path = os.path.expandvars(requirements_path)
#     requirements_path = os.path.expanduser(requirements_path)
#     requirements_path = os.path.abspath(requirements_path)

#     with open(requirements_path) as f:
#         requirements = [line.rstrip() for line in f.readlines()]



with open('requirements.txt', encoding='utf-8') as f:
    requirements = [line.rstrip() for line in f.readlines()]

setup(
    name = "dataspine-cli",
    packages = ["utils"],
    py_modules=['cli', 'model', 'predict'],
    version = __version__,
    include_package_data=True,
    description = "Dataspine CLI client",
    author = "Dataspine, Inc",
    author_email = "dev@dataspine.io",
    url = "https://github.com/dataspine",
    install_requires=requirements,
    dependency_links=[],
  entry_points='''
    [console_scripts]
    spinectl=cli:cli_commands
  ''',
)

#   entry_points='''
#     [console_scripts]
#     spinectl=cli:cli_commands
#   ''',
# )

