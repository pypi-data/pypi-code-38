#!/usr/bin/env python3
"""Setup file for boto3-service."""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boto3auth",
    version="1.0.2",
    author="Matthew Salazar",
    author_email="m@tthewsalazar.com",
    description="Simple wrapper for starting Boto3 clients/resources.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mtslzr/boto3auth",
    packages=setuptools.find_packages(),
    install_requires=[
        'boto3'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
