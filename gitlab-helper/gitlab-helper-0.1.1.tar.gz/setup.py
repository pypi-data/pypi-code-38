#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=6.0",
    "gitpython",
    "python-gitlab",
    "cookiecutter",
    "lazy_import",
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Robert Wendt",
    author_email="rwendt1337@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    description="some useful actions for interacting with gitlab",
    entry_points={"console_scripts": ["glb=glb.cli:main"]},
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="gitlab-helper",
    name="gitlab-helper",
    packages=find_packages(include=["glb"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/reedrichards/glb",
    version="0.1.1",
    zip_safe=False,
)
