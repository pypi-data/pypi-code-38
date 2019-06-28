#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from setuptools import setup, find_packages
setup(
    name = "pyharbor",
    version = "1.2.9",
    keywords = ("pyharbor", "harbor","python"),
    description = "The harbor python SDK",
    long_description = "The harbor python SDK",
    license = "MIT Licence",
    url = "https://github.com/zhangliu520/python-harbor.git",
    author = "mrzl",
    author_email = "752477168@qq.com",
    packages = ["pyharborclient"],
    platforms = "any",
    install_requires = [],

)

