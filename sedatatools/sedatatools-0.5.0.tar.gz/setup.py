#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'pandas', 'pyodbc', 'sqlalchemy']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Vedad Ramovic",
    author_email='vedad@socialexplorer.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="Tools for data team at SE.",
    entry_points={
        'console_scripts': [
            'sedatatools=sedatatools.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sedatatools',
    name='sedatatools',
    packages=find_packages(), #include=['sedatatools']
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/SocialExplorer/ContentProduction/tree/master/sedatatools',
    version='0.5.0',
    zip_safe=False,
	python_requires='>=3.5'
)
