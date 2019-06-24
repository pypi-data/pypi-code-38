#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    name='pymcs',
    version='0.1.0',
    description="Python tools for MRO MCS data analysis",
    long_description=readme + '\n\n' + history,
    author="K.-Michael Aye",
    author_email='kmichael.aye@gmail.com',
    url='https://github.com/michaelaye/pymcs',
    packages=find_packages(include=['pymcs']),
    entry_points={
        'console_scripts': [
            'pymcs=pymcs.cli:main'
        ]
    },
    package_dir={'pymcs':
                 'pymcs'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pymcs',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
