#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os.path import dirname, abspath, join, normpath, isdir
from os import listdir
import os
from tiramisu import __version__


PACKAGE_NAME = os.environ.get('PACKAGE_DST', 'tiramisu')

setup(
    version=__version__,
    author="Tiramisu's team",
    author_email='gnunux@gnunux.info',
    name=PACKAGE_NAME,
    description='an options controller tool',
    url='https://framagit.org/tiramisu/tiramisu',
    license='GNU Library or Lesser General Public License (LGPL)',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
	    "Natural Language :: English",
        "Natural Language :: French",
    ],
    long_description="""\
An options controller tool
-------------------------------------

Due to more and more available options required to set up an operating system,
compiler options or whatever, it became quite annoying to hand the necessary
options to where they are actually used and even more annoying to add new
options. To circumvent these problems the configuration control was
introduced...

Tiramisu is an options handler and an options controller, wich aims at
producing flexible and fast options access.


This version requires Python 3.5 or later.
""",
    include_package_data=True,
    packages=find_packages(include=['tiramisu'])
)
