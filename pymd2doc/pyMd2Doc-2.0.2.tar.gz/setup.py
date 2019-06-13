#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup
 
setup(
    name="pyMd2Doc",
    version="2.0.2",
    author="Yule Meng",
    author_email="88914511@qq.com",
    description="fix bug",
    long_description=open("README.rst").read(),
    license="MIT",
    url="https://github.com/yuleMeng/pyMd2Doc",
    packages=['pymd2doc'],
	include_package_data=True,
    install_requires=[
        "Markdown"
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ],
)
