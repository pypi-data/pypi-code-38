#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('hyperstools/__init__.py') as init_file:
    versions = [x for x in init_file.readlines() if '__version__' in x]
    version = versions[0].split('=')[-1].strip().strip("'")

requirements = ['boto3', 'pika>=1.0.0', 'paramiko', 'apscheduler>=3.6.0']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="hypersTools",
    author_email='drinks.huang@hypers.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    install_requires=requirements,
    include_package_data=True,
    keywords='hyperstools',
    name='hyperstools',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/drinksober/hyperstools',
    version=version,
    zip_safe=False,
)
