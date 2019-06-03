#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ 
    'numpy', 
    'scipy', 
    'pandas', 
    'matplotlib',
    'seaborn',
    'statsmodels',
    'sklearn',
    'patsy'
    ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Andrew Stewart",
    author_email='andrew.c.stewart@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Companion Python package for Fundamentals of Data Science.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fundamentals_of_data_science',
    name='fundamentals_of_data_science',
    packages=find_packages(include=['fundamentals_of_data_science']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/fundamentals-of-data-science/ds-fundamentals-python',
    version='0.1.9',
    zip_safe=False,
)
