#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple_mock",
    version="0.0.1",
    author="satyavijay shelke",
    author_email="satyavls99@gmail.com",
    description="simple patching for python functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/satyavls/simple_mock",
    packages=setuptools.find_packages(include=['simple_mock'], exclude=['simple_mock.examples',]),
    install_requires=['mock'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],

)