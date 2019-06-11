#!/usr/bin/env python
# encoding: utf-8

from sys import version_info

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["numpy", "emcee", "dill", "schwimmbad"]

if version_info < (3, 7):
    requirements.extend(["backport_ipaddress", "backports.shutil_get_terminal_size"])

setup(
    version="0.3.4",  # no need to change version number in other places.
    author="Uwe Schmitt",
    author_email="uwe.schmitt@id.ethz.ch",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Convenience layer for emcee sampler",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    name="uhammer",
    packages=find_packages(include=["uhammer"]),
    zip_safe=False,
)
