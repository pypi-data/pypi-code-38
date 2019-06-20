#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import re
from setuptools import setup, find_packages


with open(os.path.join('ndexstringloader', '__init__.py')) as ver_file:
    for line in ver_file:
        if line.startswith('__version__'):
            version=re.sub("'", "", line[line.index("'"):])

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ 'ndex2==3.0.0a1',
                 'ndexutil==0.2.0a1']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Vladimir Rynkov",
    author_email='vrynkov@ucsd.edu',
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
    description="Python Boilerplate contains all the boilerplate you need to create a Python NDEx Content Loader package.",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ndexstringloader',
    name='ndexstringloader',
    packages=find_packages(include=['ndexstringloader']),
    package_dir={'ndexstringloader': 'ndexstringloader'},
    package_data={'ndexstringloader': ['string_plan.json']},
    scripts=[ 'ndexstringloader/ndexloadstring.py'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/vrynkov/ndexstringloader',
    version=version,
    zip_safe=False,
)
