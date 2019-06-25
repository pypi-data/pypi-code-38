#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Created by Roberto Preste
from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["pysam>=0.10.0", ]

setup_requirements = ["pytest-runner", ]

test_requirements = ["pytest", ]

setup(  # pragma: no cover
    author="Roberto Preste",
    author_email="robertopreste@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Python 3 VCF library, based on vcfpy.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="vcfpy2",
    name="vcfpy2",
    packages=find_packages(include=["vcfpy2"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/robertopreste/vcfpy2",
    version='0.1.2',
    zip_safe=False,
)
