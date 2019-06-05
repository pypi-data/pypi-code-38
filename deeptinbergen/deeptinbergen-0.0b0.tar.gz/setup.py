#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepTinbergen
A Mathis, alexander.mathis@bethgelab.org
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deeptinbergen",
    version="0.0.b0",
    author="Alexander Mathis",
    author_email="alexander.mathis@bethgelab.org",
    description="abc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlexEMG/DeepTinbergen",
    install_requires=['easydict~=1.7'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ),
    entry_points="""[console_scripts]
            dlc=dlc:main""",
)

