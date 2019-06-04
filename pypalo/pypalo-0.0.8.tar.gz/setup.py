#!/usr/bin/env python
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
"""
A distutils Python setup file. For setuptools support see setup_egg.py.
"""
from setuptools import setup, find_packages

keywords = ['palo alto', 'paloalto', 'pan', 'panorama']

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pypalo",
    version="0.0.8",
    author="Donald Stogsdill",
    author_email="donny.stogsdill@gmail.com",
    description="A Package to interact with the Palo Alto Networks API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dstogsdill/pypalo",
    packages=find_packages(),
    install_requires=['pan-python', 'xmltodict', ],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
