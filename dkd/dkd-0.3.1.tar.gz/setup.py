#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Dao-Ke-Dao
    ~~~~~~~~~~

    Common Message Module for decentralized instant messaging
"""

from setuptools import setup, find_packages

__version__ = '0.3.1'
__author__ = 'Albert Moky'
__contact__ = 'albert.moky@gmail.com'

with open('README.md', 'r') as fh:
    readme = fh.read()

setup(
    name='dkd',
    version=__version__,
    url='https://github.com/dimchat/dkd-py',
    license='MIT',
    author=__author__,
    author_email=__contact__,
    description='A common message module',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
    ]
)
