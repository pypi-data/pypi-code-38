#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import pypandoc

pypandoc.convert_file("README.md", "rst", outputfile="README.rst")
setup(
    name="transmission-popgen",
    version="0.0.9",
    py_modules=["transmission"],
    description=(
        "Tools for inferring symbiont transmission mode from"
        "metagenomic data"
    ),
    url="http://github.com/mpjuers/transmission",
    author="Mark Juers",
    author_email="mpjuers@indiana.edu",
    license="GPL>=3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "msprime", "numpy", "rpy2", "tqdm"],
    entry_points="""
        [console_scripts]
        transmission-priorgen=transmission.cli_tools:simulate_prior_stats
    """,
    zip_safe=False,
)
