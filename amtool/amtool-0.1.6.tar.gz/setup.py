#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0',
                'click_log>=0.3.2',
                'click_plugins>=1.1.1',
                'PyYAML>=5.1']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Kenneth E. Bellock",
    author_email='ken@bellock.net',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="The Artifacts Management Tool is meant to be a generic means of storing and manipulating artifact data in a human readable text format ideal for colaborative work.",
    entry_points={
        'console_scripts': [
            'amt=amt.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='amtool',
    name='amtool',
    packages=find_packages(include=['amtool']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/bellockk/amtool',
    version='0.1.6',
    zip_safe=False,
)
