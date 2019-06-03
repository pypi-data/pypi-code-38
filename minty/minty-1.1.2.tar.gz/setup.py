#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

with open("requirements/base.txt") as f:
    requirements = f.read().splitlines()

with open("requirements/test.txt") as f:
    test_requirements = f.read().splitlines()

setup(
    author="Michiel Ootjers",
    author_email="michiel@mintlab.nl",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Minty Command and Query based on DDD",
    setup_requires=["pytest-runner"],
    install_requires=requirements,
    license="EUPL license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="minty",
    name="minty",
    packages=find_packages(include=["minty", "minty.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://gitlab.com/minty-python/minty",
    version="1.1.2",
    zip_safe=False,
)
