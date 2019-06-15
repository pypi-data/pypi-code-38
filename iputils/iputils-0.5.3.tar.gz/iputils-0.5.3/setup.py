#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# date:        2019/6/6
# author:      he.zhiming
#

from __future__ import (absolute_import, unicode_literals)

from setuptools import setup
import codecs

setup(
    name="iputils",
    version="0.5.3",
    platforms="any",
    url="https://github.com/hezhiming/iputils",
    license="MIT",
    author="he.zhiming",
    author_email="he.zhiming@foxmail.com",
    description="wrapper of ipaddress.py, easy to use",
    long_description=codecs.open("README.rst", encoding="utf-8", mode="r").read(),
    keywords="IPv4, IPv6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)
