#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

with open("README.md") as fp:
    long_description = fp.read()

setup(
    name="py-registry",
    version="0.1.2",
    description="Python Class Registry",
    long_description=long_description,
    author="Hasan Basri",
    author_email="hbasria@gmail.com",
    license="MIT",
    keywords="Python Class Registry",
    url="https://github.com/hbasria/py-registry",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["py-dictutils~=0.1"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite="tests",
)
