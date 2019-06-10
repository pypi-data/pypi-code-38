#!/usr/bin/env python
# gen_pkg_manifest.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import sys

# Intra-package imports
import pypkg.functions


###
# Functions
###
if __name__ == "__main__":
    print("Generating MANIFEST.in file")
    pypkg.functions.gen_manifest("wheel" in sys.argv)
