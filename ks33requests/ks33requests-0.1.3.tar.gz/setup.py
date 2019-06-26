#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""setuptools script of this package

see:

* https://packaging.python.org/
* https://setuptools.readthedocs.io/
"""
from setuptools import setup

setup(
    use_scm_version={
        # guess-next-dev:	automatically guesses the next development version (default)
        # post-release:	generates post release versions (adds postN)
        'version_scheme': 'guess-next-dev',
        'write_to': 'src/ks33requests/_scm_version.py',
    },
)
