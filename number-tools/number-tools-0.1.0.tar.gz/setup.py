#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
from setup_utils import read, read_markdown

PACKAGE_NAME = "number-tools"
PACKAGE_ROOT_NAME = "number_tools"
GITHUB_URL = "https://github.com/alexseitsinger/{}".format(PACKAGE_NAME)
HOMEPAGE_URL = "https://www.alexseitsinger.com/packages/python/{}".format(PACKAGE_NAME)
README_NAME = "README.md"

setup(
    name=PACKAGE_NAME,
    version=read(("src", PACKAGE_ROOT_NAME, "__init__.py"), "__version__"),
    description=read_markdown((README_NAME,), "Description", (0,)),
    long_description=read((README_NAME,)),
    long_description_content_type="text/markdown",
    author="Alex Seitsinger",
    author_email="software@alexseitsinger.com",
    url=HOMEPAGE_URL,
    package_dir={"": "src"},
    packages=find_packages("src", exclude=["tests"]),
    include_package_data=True,
    license="BSD 2-Clause License",
    keywords=["numbers"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": HOMEPAGE_URL,
        "Source": GITHUB_URL,
        "Tracker": "{}/issues".format(GITHUB_URL),
    },
)
