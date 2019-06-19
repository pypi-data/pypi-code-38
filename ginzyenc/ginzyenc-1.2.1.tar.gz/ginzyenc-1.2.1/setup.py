#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension

setup(
    name            = "ginzyenc",
    version         = "1.2.1",
    author          = "dermatty",
    author_email    = "stephan@untergrabner.at",
    url             = "https://github.com/dermatty/GINZYENC",
    license         = "LGPLv3",
    package_dir     = {'ginzyenc': 'src'},
    ext_modules     = [Extension("ginzyenc", ["src/ginzyenc.c"])],
    classifiers     = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: C",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: Unix",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Usenet News"
    ],
    description     = "yEnc Module for Python modified for SABnzbd",
    long_description = """
yEnc Decoding for Python 3.7
---------------------------------

Mofied the original yenc module by Alessandro Duca & saphirefor use within ginzibix.

The module was extended to do header parsing and full yEnc decoding from a Python
list of chunks, the way in which data is retrieved from usenet.

Currently CRC-checking of decoded data is disabled to allow for increased performance.
It can only be re-enabled by locally altering 'sabyenc.h' and setting 'CRC_CHECK 1'.
"""
)

