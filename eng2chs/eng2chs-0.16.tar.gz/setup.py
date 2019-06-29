#!/usr/bin/env python  
from __future__ import print_function
from setuptools import setup, find_packages
import sys
#python setup.py sdist upload
setup(
    name="eng2chs",
    version="0.16",
    author="smvlboy",
    author_email="smvlboy@outlook.com",
    description="a moudle used to translate english to chinese",
    url="https://pypi.org/project/eng2chs/#description",
    install_requires=[
        'urllib3','requests','bs4','PyExecJS'
    ],
packages=['eng2chs'],
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)  