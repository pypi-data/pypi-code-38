#!/usr/bin/env python
# -*- coding: utf-8 -*-

#                                                           
# Copyright (C)2017 SenseDeal AI, Inc. All Rights Reserved  
#                                                           

"""                                                   
File: setup.py
Author: lzl
E-mail: zll@sensedeal.ai
Last modified: 2019/4/4
Description:                                              
"""

from setuptools import setup

requirements = [
    "lxml",
]

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name='sense-html',
    version='1.1.2',
    packages=[
        "sense_html",
    ],
    license='BSD License',
    description='sense html handle',
    install_requires=requirements,
    long_description='',
    long_description_content_type="text/markdown",
    url='',
    author='kafka0102',
    author_email='yujianjia@sensedeal.ai',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
