#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

from pathlib import Path

from setuptools import find_namespace_packages, setup


# Package meta-data.
NAME = 'nv.utils'
NAMESPACE = 'nv'
DESCRIPTION = 'Parsers, formatters, data structures and other helpers for Python 3.'
URL = 'https://github.com/gstos/nv-utils'
EMAIL = 'gustavo@next.ventures'
AUTHOR = 'Gustavo Santos'
REQUIRES_PYTHON = '>=3.6'

# What packages are required for this module to be executed?
REQUIRED = [
    'pytz'
]

# What packages are optional?
EXTRAS = {
    'vault': ['hvac'],
    'tables': ['openpyxl', 'xlwt', 'xlrd'],
    'xlsx': ['openpyxl'],
    'xls': ['xlrd', 'xlwt'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = Path(__file__).resolve().parent


def read_txt(path, default=None):
    try:
        with path.open(mode='r', encoding='utf-8') as fp:
            return fp.read()
    except FileNotFoundError:
        return default


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
long_description = read_txt(here / 'README.md', default=DESCRIPTION)
changes = read_txt(here / 'CHANGES.md', default=None)

if changes:
    long_description = long_description + '\n' + changes

version = read_txt(here / 'VERSION.txt', default=None)

if version is None:
    raise SystemExit(f'Add VERSION.txt to project root')


# Where the magic happens:
setup(
    name=NAME,
    namespace_packages=[NAMESPACE],
    version=version,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_namespace_packages(include=[f'{NAMESPACE}.*'], exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
