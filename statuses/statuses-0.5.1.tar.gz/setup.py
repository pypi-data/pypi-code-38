#!/usr/bin/env python
import os
from setuptools import setup, find_packages

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "README.md")
) as file:  # noqa
    long_description = file.read()

setup(
    name="statuses",
    author="chrisdotcode",
    author_email="pypi+chris@code.sc",
    url="https://github.com/chrisdotcode/statuses",
    description="The `Status` class represents the status of some event.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    license="BSD 3-Clause License",
    packages=find_packages(exclude=["tests"]),
    package_data={"statuses": ["py.typed"]},
    zip_safe=False,
    install_requires=[],
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    test_suite="tests",
)
