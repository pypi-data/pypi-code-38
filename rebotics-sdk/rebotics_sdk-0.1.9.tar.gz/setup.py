#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup_requirements = ['pytest-runner', ]
test_requirements = ['pytest', ]

setup(
    author="Malik Sulaimanov",
    author_email='malik@retechlabs.com',
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
    description="Rebotics SDK for communicating with Rebotic Services, API CLI client.",
    entry_points={
        'console_scripts': [
            'admin=rebotics_sdk.cli.admin:api',
            'dataset=rebotics_sdk.cli.dataset:api',
            'retailer=rebotics_sdk.cli.retailer:api',
            'rebotics=rebotics_sdk.cli.common:main',
        ],
    },
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='rebotics_sdk',
    name='rebotics_sdk',
    packages=find_packages(),
    test_suite='tests',
    url='http://retechlabs.com/rebotics/',
    version='0.1.9',
    zip_safe=False,
    install_requires=[
        'requests==2.21.0',
        'six>=1.12.0',
    ],
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require={
        'hook': [
            'django',
            'djangorestframework'
        ],
        'shell': [
            'ipython>=7.5.0,<8',
            'pandas',
            'pytz',
            'ptable',
            'python-dateutil',
            'humanize',
            'PySocks!=1.5.7,>=1.5.6',
            'requests[socks]',
            'requests-toolbelt>=0.9.1',
            'tqdm',
            'xlrd>=1.2.0',
            'click>=7.0',
        ]
    }
)
