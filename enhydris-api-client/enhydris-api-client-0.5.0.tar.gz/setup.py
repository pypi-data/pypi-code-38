#!/usr/bin/env python

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["iso8601", "pandas>=0.20", "requests>=1,<3", "htimeseries>=1.1.1,<2"]

setup_requirements = []

test_requirements = []

setup(
    author="Antonis Christofides",
    author_email="antonis@antonischristofides.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    description="Python API client for Enhydris",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    name="enhydris-api-client",
    packages=find_packages(include=["enhydris_api_client"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/openmeteo/enhydris-api-client",
    version="0.5.0",
    zip_safe=False,
)
