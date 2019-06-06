#!/usr/bin/env python3

from setuptools import setup, find_packages
import re

# Detect version
with open('restomatic/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]',
                        f.read(), re.MULTILINE).group(1)

with open('README.md', 'r') as f:
    long_description = f.read()

if not version:
    raise RuntimeError('Internal Error: Unable to find version information')

setup(
    name='restomatic',
    version=version,
    description='Automatic JSON-based API generator, including a SQL Query Compositor and WSGI Endpoint Router',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/dtulga/restomatic',
    author='David Tulga',
    author_email='davidtulga@gmail.com',
    license='MIT',
    py_modules=['restomatic'],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
