#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['prettytable==0.7.2', 'python-magic==0.4.15', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="hnp",
    author_email='hobnobpirate@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Checks to see if magic number contents of files match extensions. Mostly a CTF tool.",
    entry_points={
        'console_scripts': [
            'examine_files=examine_files.examine_files:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='examine_files',
    name='examine_files',
    packages=find_packages(include=['examine_files']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/hobnobpirate/examine_files',
    version='0.1.0',
    zip_safe=False,
)
