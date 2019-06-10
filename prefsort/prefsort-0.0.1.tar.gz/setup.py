#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open

with open('README.rst', encoding='utf-8') as readme_file:
    readme = readme_file.read()

test_requirements = [
    'tox',
    'pytest',
    'coverage',
    'pytest-cov'
]

setup(
    name='prefsort',
    version='0.0.1',
    description="Sort a sequence, preferring some values",
    long_description=readme,
    author="Jonathan Eunice",
    author_email='jonathan.eunice@gmail.com',
    url='https://github.com/jonathaneunice/prefsort',
    packages=[
        'prefsort',
    ],
    package_dir={'prefsort':
                 'prefsort'},
    include_package_data=True,
    install_requires=[],
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='prefsort',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='test',
    tests_require=test_requirements
)
