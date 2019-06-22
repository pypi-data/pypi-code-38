"""Pip installation script for `spatial_sites`."""

import os
import re
from setuptools import find_packages, setup


def get_version():

    ver_file = '{}/_version.py'.format('spatial_sites')
    with open(ver_file) as handle:
        ver_str_line = handle.read()

    ver_pattern = r'^__version__ = [\'"]([^\'"]*)[\'"]'
    match = re.search(ver_pattern, ver_str_line, re.M)
    if match:
        ver_str = match.group(1)
    else:
        msg = 'Unable to find version string in "{}"'.format(ver_file)
        raise RuntimeError(msg)

    return ver_str


def get_long_description():

    readme_file = 'README.md'
    with open(readme_file, encoding='utf-8') as handle:
        contents = handle.read()

    return contents


setup(
    name='spatial-sites',
    version=get_version(),
    description=('A package to represent labelled, spatial coordinates.'),
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Adam J. Plowman',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    project_urls={
        'Github': 'https://github.com/aplowman/spatial-sites',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Physics',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ]
)
