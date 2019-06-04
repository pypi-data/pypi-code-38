"""Akeyless SDK for Python."""

import os
import re

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")


def read(*args):
    """Reads complete file contents."""
    return open(os.path.join(HERE, *args)).read()


def get_requirements():
    """Reads the requirements file."""
    requirements = read("requirements.txt")
    return [r for r in requirements.strip().splitlines()]


def get_version():
    """Reads the version from this module."""
    init = read("src", "akeyless", "__init__.py")
    return VERSION_RE.search(init).group(1)


setup(
    name="akeyless",
    packages=find_packages("src"),
    package_dir={"": "src"},
    version=get_version(),
    description="Akeyless SDK implementation for Python",
    author="Akeyless Security",
    maintainer="Akeyless Security",
    author_email="refael@akeyless-security.com",
    url="https://github.com/akeylesslabs/akeyless-python-sdk-examples",
    keywords=["Akeyless", "akeyless sdk", "encryption"],
    license="Apache License 2.0",
    install_requires=get_requirements(),
    include_package_data=True,
    long_description=read("README.rst"),
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
    ],
)
