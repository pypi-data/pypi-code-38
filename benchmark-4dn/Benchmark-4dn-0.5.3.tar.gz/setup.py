#!/usr/bin/env python
# The Github repo for this project is:
# https://github.com/SooLee/Benchmark
# IMPORTANT: use Python 2.7 or above for this package

import io
from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="Benchmark-4dn",
    version=open("Benchmark/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    description="Benchmark functions that returns total space, mem, cpu given \
                input size and parameters for the CWL workflows",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/SooLee/Benchmark/",
    author="Soo Lee",
    author_email="duplexa@gmail.com",
    license="MIT",
    keywords=['benchmark', 'cwl', 'common workflow language',
              'docker', 'tibanna', 'bioinformatics', '4dn'],
    packages=find_packages(),
    package_data={"": ["aws/*"]},
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
