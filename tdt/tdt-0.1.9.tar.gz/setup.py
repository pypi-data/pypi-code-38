import os
import re
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

name = 'tdt'
with open('{}/__init__.py'.format(name), 'r') as file:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        file.read(), re.MULTILINE).group(1)

setup(
    name=name,
    version=version,
    author="Mark Hanus",
    author_email="mhanus@tdt.com",
    description="Tucker-Davis Technologies (TDT) Python APIs for reading data and interacting with Synapse software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    packages=find_packages(),
    install_requires = ['numpy']
)