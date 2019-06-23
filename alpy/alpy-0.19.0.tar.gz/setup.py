#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import setuptools

import alpy

setuptools.setup(
    name="alpy",
    version=alpy.__version__,
    description="Library for testing network virtual appliances using Docker",
    url="https://gitlab.com/abogdanenko/alpy",
    packages=["alpy"],
    install_requires=["docker", "pexpect", "qmp"],
    author="Alexey Bogdanenko",
    author_email="alexey@bogdanenko.com",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
)
