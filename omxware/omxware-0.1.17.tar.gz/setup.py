#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['python-keycloak>=0.16.0',
                'simplejson>=3.16.0',
                'pprint',
                'pandas',
                'configparser',
                'requests',
                'urllib3<=1.24.2',
                'IPython',
                'matplotlib',
                'pycrypto'
                ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Harsha Krishnareddy",
    author_email='hvkrishn@us.ibm.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python wrapper for OMXWare REST services to access Data and Files.",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='omxware',
    # Platform='unix',
    name='omxware',
    packages=find_packages(include=['omxware', 'omxware.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.ibm.com/GrandChallenge-Almaden/omxware-pypi',
    version='0.1.17',
    zip_safe=False,
    exclude_package_data={'': ['README.rst', 'Makefile', '.travis.yml']},
)
