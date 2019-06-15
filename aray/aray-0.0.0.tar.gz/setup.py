#!/usr/bin/env python
# Based on:
# https://packaging.python.org/tutorials/packaging-projects/

import setuptools

setuptools.setup(
    name="aray",
    version="0.0.0",
    author="A Ray",
    author_email="a@machinaut.com",
    description="Public personal python package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/machinaut/aray",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
