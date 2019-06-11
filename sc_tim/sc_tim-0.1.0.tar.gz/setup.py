#!/usr/bin/env python

from __future__ import print_function
from setuptools import setup, find_packages
import sys
 
setup(
		name="sc_tim",
		version="0.1.0",
		author="Zhanying Feng",
		author_email="zyfeng@amss.ac.cn",
		description="scTIM is a convenient tool for cell-type indicative marker detection based on single cell RNA-seq data",
		long_description=open("README.rst").read(),
		license="AMSS",
		url="https://github.com/Frank-Orwell/scTIM",
		packages=find_packages(),
		install_requires=[
			"numpy",
			],
		classifiers=[
			"Programming Language :: Python",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.5",
		],
)

