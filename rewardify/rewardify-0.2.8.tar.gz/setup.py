#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


# 08.06.2019
# We are using peewee as the ORM to access the database
# argon2 provides the secure hashing algorithm to handle password hashing
requirements = [
    'Click>=6.0',
    'peewee>=3.9',
    'cffi>=1.12'
    'argon2>=0.1.0',
    'argon2_cffi>=19.0',
    'numpy',
    'pandas'
]

setup_requirements = requirements + ['pytest-runner', ]

test_requirements = requirements + ['pytest', ]

setup(
    author="Jonas Teufel",
    author_email='jonseb1998@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Base frame reward system",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='rewardify',
    name='rewardify',
    packages=find_packages(include=[
        'rewardify',
        'rewardify.backends',
        'rewardify.templates'
    ]),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/the16thpythonist/rewardify-base.git',
    version='0.2.8',
    zip_safe=False,
)
