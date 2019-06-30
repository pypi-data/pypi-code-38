from setuptools import setup, find_packages

import os

with open("README.md") as f:
    long_desc = f.read()

here = os.path.abspath(os.path.dirname(__file__))
info = {}
pkg_name = "kotano"

with open(
        os.path.join(here, pkg_name, "__init__.py")) as f:
    exec(f.read(), None, info)

setup(
        name=pkg_name,
        version=info['__version__'],
        description=info['__description__'],
        long_description=long_desc,
        long_description_content_type="text/markdown",
        author=info['__author__'],
        author_email=info['__author_email__'],
        url="https://github.com/tripleko-llc/kotano",
        packages=find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ],
        )

