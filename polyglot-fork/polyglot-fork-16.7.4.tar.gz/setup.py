#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import io

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with io.open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with io.open('HISTORY.rst', 'r', encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

with io.open('requirements.txt', 'r') as f:
    packages = set(f.read().splitlines())

requirements = list(filter(lambda x: "http" not in x, packages))

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='polyglot-fork',
    version='16.07.04',
    description='Polyglot is a natural language pipeline that supports massive multilingual applications.',
    long_description="fork of polyglot",
    author='Rami Al-Rfou',
    author_email='rmyeid@gmail.com',
    url='https://github.com/aboSamoor/polyglot',
    packages = ['polyglot',
                'polyglot.detect',
                'polyglot.tokenize',
                'polyglot.mapping',
                'polyglot.tag',
                'polyglot.transliteration'],
    entry_points={
        'console_scripts': [
            'polyglot = polyglot.__main__:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3",
    zip_safe=False,
    keywords='polyglot',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
