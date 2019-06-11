#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

with open("cgecore/__init__.py", 'r') as f:
    for l in f:
        if l.startswith('__version__'):
            version = l.split('=')[1].strip().strip('"')

setup(
   name='cgecore',
   version=version,
   description='Center for Genomic Epidemiology Core Module',
   long_description=long_description,
   license="Apache License, Version 2.0",
   author='Martin Thomsen',
   author_email='mcft@bioinformatics.dtu.dk',
   url="https://bitbucket.org/genomicepidemiology/cge_core_module",
   packages=['cgecore', 'cgecore.blaster']
)
