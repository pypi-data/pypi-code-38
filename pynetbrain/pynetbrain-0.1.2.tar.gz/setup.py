#!/usr/bin/env python
# -*- coding: utf-8 -*-

# For a fully annotated version of this file and what it does, see
# https://github.com/pypa/sampleproject/blob/master/setup.py

# To upload this file to PyPI you must build it then upload it:
# python setup.py sdist bdist_wheel  # build in 'dist' folder
# python-m twine upload dist/*  # 'twine' must be installed: 'pip install twine'

from setuptools import setup
import pynetbrain

with open("README.md", "r") as f:
     ldesc = f.read()

setup(name="pynetbrain",
     version=pynetbrain.__version__,
     author="Brady Lamprecht",
     author_email="bdlamprecht@gmail.com",
     url="",
     py_modules=["pynetbrain"],
     description="A client library for interacting with NetBrain7 API",
     long_description=ldesc,
     license="MIT",
     python_requires=">=3.6",
     install_requires=["requests>=2.20.0"],
     zip_safe=False,
     keywords=['netbrain'],
     classifiers=["Programming Language :: Python :: 3"],
     )
