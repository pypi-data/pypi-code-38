# -*- coding: utf-8 -*-

from __future__ import absolute_import
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="aiida-export-migration-tests",
    version="0.5.0",
    author="The AiiDA team",
    author_email="developers@aiida.net",
    description="Export migrations tests for AiiDA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aiidateam/aiida-export-migration-tests",
    packages=find_packages(),
    license="MIT Licence",
    include_package_data=True)
