#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Click>=6.0", "attrs>=19.1.0", "feedgen>=0.7.0", "pyyaml>=5.1"]

setup_requirements = []

test_requirements = []

setup(
    author="Cristóbal Carnero Liñán",
    author_email="ccarnerolinan@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Static podcast generator.",
    entry_points={"console_scripts": ["podenco=podenco.podenco:main"]},
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="podenco",
    name="podenco",
    packages=find_packages(include=["podenco"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/cristobalcl/podenco",
    version="0.0.2",
    zip_safe=False,
)
