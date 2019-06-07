#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-annie",
    version="0.1.4",
    description="Singer.io tap for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_annie"],
    install_requires=[
        "singer-python>=5.0.12",
        "requests",
        "google-auth",
        "google-cloud",
        "google-cloud-bigquery"
    ],
    entry_points="""
    [console_scripts]
    tap-annie=tap_annie:main
    """,
    packages=["tap_annie"],
    package_data = {
        "schemas": ["tap_annie/schemas/*.json"]
    },
    include_package_data=True,
)
