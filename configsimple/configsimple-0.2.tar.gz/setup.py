#!/usr/bin/env python
# encoding: utf-8

"""Packaging script for the configsimple library."""

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    readme = f.read()

setup(
    name="configsimple",
    version="0.2",
    author="Johann Petrak",
    author_email="johann.petrak@gmail.com",
    description='Configure components/classes using config files, command line options etc in a simple way',
    long_description=readme,
    long_description_content_type='text/markdown',
    setup_requires=["pytest-runner"],
    install_requires=[],
    python_requires=">=3.5",
    tests_require=['pytest'],
    platforms='any',
    license="MIT",
    keywords="",
    url="http://github.com/johann-petrak/configsimple",
    packages=find_packages(),
    test_suite='tests',
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        # "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Intended Audience :: Developers",
      ],
)
