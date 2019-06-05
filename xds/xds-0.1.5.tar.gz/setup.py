#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Xuan Ma
# Mail: xuan.ma1@northwestern.edu
#############################################

from setuptools import setup, find_packages

setup(
    name = "xds",
    version = "0.1.5",
    keywords = ("xds", "NOMAD","data loading"),
    description = "Loading xds structure",
    long_description = "Python codes for loading xds data structure",
    license = "MIT Licence",

    url = "https://github.com/xuanma/xds",    
    author = "Xuan Ma",
    author_email = "xuan.ma1@northwestern.edu",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["scipy"] 
)