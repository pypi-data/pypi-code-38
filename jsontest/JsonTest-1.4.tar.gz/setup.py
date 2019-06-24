#!/usr/bin/env python
# JsonTest
# File: setup.py
# Desc: needed

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    version='1.4',
    name='JsonTest',
    description='A tiny metaclass for autogenerating tests from JSON files',
    author='Nick Barrett',
    author_email='pointlessrambler@gmail.com',
    url='http://github.com/Fizzadar/JsonTest',
    py_modules=['jsontest'],
)
