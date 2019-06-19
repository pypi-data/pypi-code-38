#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='pykvf',
    version='0.1.17',
    description='null',
    author='banixc',
    author_email='banixc@gamil.com',
    url=' ',
    py_modules=['pykvf'],
    packages=find_packages(),
    install_requires=[
        'pymysql',
        'toml'
    ],
)
