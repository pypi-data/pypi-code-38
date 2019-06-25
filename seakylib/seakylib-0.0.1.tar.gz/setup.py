#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2019/6/25 16:07


import setuptools

import seakylib

with open("README.md", "r") as fh:
    long_description = fh.read()

print(setuptools.find_packages())

setuptools.setup(
    name=seakylib.__title__,
    version=seakylib.__version__,
    author=seakylib.__author__,
    author_email='seaky.cn@gmail.com',
    description='seaky\'s private lib',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url='',
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
