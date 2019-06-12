#!/usr/bin/env python
import io

from bassoon.Version import version

from setuptools import find_packages, setup


readme = io.open('README.md', 'r', encoding='utf-8').read()

setup(
    name='bassoon',
    description='A simple get-config-from-env class',
    long_description=readme,
    url='https://github.com/Vesuvium/bassoon',
    author='Jacopo Cascioli',
    author_email='noreply@jacopocascioli.com',
    version=version,
    license='MPL 2.0',
    packages=find_packages(),
    tests_require=[
        'pytest>=4.3.1',
        'pytest-cov>=2.6.1',
        'pytest-mock>=1.10.1'
    ],
    setup_requires=[],
    install_requires=[],
    classifiers=[]
)
