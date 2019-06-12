#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import re
from setuptools import setup, find_packages

with open(os.path.join('ndexncipidloader', '__init__.py')) as ver_file:
    for line in ver_file:
        if line.startswith('__version__'):
            version=re.sub("'", "", line[line.index("'"):])

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ 'ndex2',
                 'ndexutil',
                 'biothings_client',
                 'ftpretty',
                 'requests',
                 'pandas']

setup_requirements = [ ]

test_requirements = [
    "requests-mock",
    "mock"
]

setup(
    author="Chris Churas",
    author_email='contact@ndexbio.org',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Loads NCI-PID data into NDEx",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ndexncipidloader',
    name='ndexncipidloader',
    packages=find_packages(include=['ndexncipidloader']),
    package_dir={'ndexncipidloader': 'ndexncipidloader'},
    package_data={'ndexncipidloader': [ 'loadplan.json',
                                        'networkattributes.tsv',
                                        'style.cx',
                                        'gene_symbol_mapping.json']},
    scripts=[ 'ndexncipidloader/loadndexncipidloader.py'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ndexcontent/ndexncipidloader',
    version=version,
    zip_safe=False,
)
