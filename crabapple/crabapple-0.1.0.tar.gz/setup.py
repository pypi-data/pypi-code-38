#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: soukon
# Mail: 417993072@qq.com
# Created Time:  2019-6-17
#############################################


from setuptools import setup, find_packages

setup(
    name = "crabapple",
    version = "0.1.0",
    keywords = ("pip", "crabapple","Crabapple", "CrabappleJson"),
    description = "Json algorithm based on groupby",
    long_description = "Json algorithm based on groupby",
    license = "MIT Licence",

    url = "https://github.com/soukon9/crabapple",
    author = "crabapple",
    author_email = "417993072@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
