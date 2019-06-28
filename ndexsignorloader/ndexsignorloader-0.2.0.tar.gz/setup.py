#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import re
from setuptools import setup, find_packages


with open(os.path.join('ndexsignorloader', '__init__.py')) as ver_file:
    for line in ver_file:
        if line.startswith('__version__'):
            version=re.sub("'", "", line[line.index("'"):])

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['ndex2',
                'ndexutil',
                'requests',
                'pandas']

setup_requirements = [ ]

test_requirements = ['requests-mock',
                     'mock']

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
    description="Loads SIGNOR data into NDEx",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ndexsignorloader',
    name='ndexsignorloader',
    packages=find_packages(include=['ndexsignorloader']),
    package_dir={'ndexsignorloader': 'ndexsignorloader'},
    package_data={'ndexsignorloader': ['loadplan.json',
                                       'style.cx']},
    scripts=[ 'ndexsignorloader/ndexloadsignor.py'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ndexcontent/ndexsignorloader',
    version=version,
    zip_safe=False,
)
