#!/usr/bin/env python
# coding: utf-8
import sys
from setuptools import setup, find_packages

requires = [
    'awscli>=1.16.140',
]

setup(
    name='awscli-sqsall',
    version="1.0.0",
    description='awscli pulgin to treat SQS queues more like files',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Paulo Köch',
    author_email='paulo.koch@gmail.com',
    url='https://github.com/pkoch/awscli-sqsall',
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=requires,
)
