#!/usr/bin/env python
# coding: utf-8

import os
import re
from setuptools import setup, find_packages

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

here = os.path.abspath(os.path.dirname(__file__))

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)


def load_readme():
    with open(os.path.join(here, 'README.md')) as f:
        return f.read()


setup(
    name='__yourapp',
    version=re.search(
        r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
        open('__yourapp/main.py').read()).group(1),
    description='TODO: description',
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    author='__yourname',
    author_email='__youraddress',
    maintainer='__yourname',
    maintainer_email='__youraddress',
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements,
    extras_require={'test': test_requirements},
    entry_points={
        'console_scripts': [
            '__yourapp = __yourapp.main:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
