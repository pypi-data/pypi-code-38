#!/usr/bin/env python
import os
from setuptools import setup, find_packages

base = os.path.dirname(os.path.abspath(__file__))

README_PATH = os.path.join(base, "README.rst")

install_requires = ["packaging"]

tests_require = []

setup(
    name="vcver",
    version="0.2.0",
    description="provide package versions with version control data.",
    long_description=open(README_PATH).read(),
    author="Yusuke Tsutsumi",
    author_email="yusuke@tsutsumi.io",
    url="https://github.com/toumorokoshi/vcver-python",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Software Distribution",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],
    tests_require=tests_require,
    entry_points={
        "distutils.setup_keywords": ["vcver=vcver:setup_keywords_entry_point"]
    },
)
