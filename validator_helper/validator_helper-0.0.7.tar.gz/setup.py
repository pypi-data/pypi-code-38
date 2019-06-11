#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="validator_helper",
    version="0.0.7",
    packages=find_packages(),
    author="Andrew Low",
    author_email="andrew.low@canada.ca",
    url="https://github.com/lowandrew/Validator_Helper",
    install_requires=['pandas',
                      'numpy',
                      'pytest'],
)
