#!/usr/bin/env python3
#-*- coding:utf-8 -*-
 
#############################################
# File Name: setup.py
# Author: xiaoyao 
# Mail: xiaoyaoalpha@gmail.com
# Created Time: 2019-4-29 11:17:34
#############################################
 
 
from setuptools import setup, find_packages
 
setup(
  name = "punittest",
  version = "0.1.8",
  keywords = ("pip", "punittest"),
  description = "An extented unittest",
  long_description = "An extented unittest",
  license = "",
 
  url = "http://www.google.com",
  author = "xiaoyao",
  author_email = "xiaoyaoalpha@gmail.com",
 
  packages = find_packages(),
  include_package_data = True,
  platforms = "any",
  install_requires = [
    "openpyxl==2.5.2",
  ]
)