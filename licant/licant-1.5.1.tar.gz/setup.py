#!/usr/bin/env python3

from setuptools import setup
import glob
import os

import licant

setup(
    name="licant",
    packages=["licant"],
    version=licant.__version__,
    license="MIT",
    description="licant make system",
    author="Sorokin Nikolay",
    author_email="mirmikns@yandex.ru",
    url="https://github.com/mirmik/licant",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    keywords=["testing", "make"],
    classifiers=[],
    scripts=["configurator/licant-libs"],
    # 	package_data={'licant': [
    #   	'templates/cxx/make.py',
    # 	  	'templates/cxx/main.cpp',
    # 	 	'templates/cxxgxx/make.py',
    # 		'templates/cxxgxx/main.cpp',
    #    ]}
)
