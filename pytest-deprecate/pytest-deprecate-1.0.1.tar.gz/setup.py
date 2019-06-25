#!/usr/bin/env python

from os.path import isfile

from setuptools import setup


def _read_file(path):
    with open(path) as fp:
        return fp.read().strip()


PROJECT_VERSION = _read_file("VERSION.txt")

REQUIREMENTS = _read_file("requirements.txt").split("\n")
DEV_REQUIREMENTS = _read_file("requirements_dev.txt").split("\n")


if isfile("README.md"):
    long_description = _read_file("README.md")
else:
    long_description = ""

setup(
    name="pytest-deprecate",
    author="NyanKiyoshi",
    author_email="hello@vanille.bid",
    url="https://github.com/NyanKiyoshi/pytest-deprecate/",
    description="Mark tests as testing a deprecated feature with a warning note.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=PROJECT_VERSION,
    packages=["pytest_deprecate"],
    entry_points={"pytest11": ["pytest_deprecate = pytest_deprecate.plugin"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Pytest",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=REQUIREMENTS,
    extras_require={"dev": DEV_REQUIREMENTS},
    zip_safe=False,
)
