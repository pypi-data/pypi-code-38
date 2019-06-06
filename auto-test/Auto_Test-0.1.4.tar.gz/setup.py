#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name = "Auto_Test",
    version = "0.1.4",
    author = "IcyDong",
    author_email = "xxxx@qq.com",
    description = "Interface Automation Testing",
    long_description = open("README.rst").read(),
    license = "MIT",
    url = "https://github.com",
    packages = ['AutoTest'],
    install_requires = ["requests","BlueTest"],
    classifiers = [
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Topic :: Text Processing :: Indexing",
    "Topic :: Utilities",
    "Topic :: Internet",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    ],
)