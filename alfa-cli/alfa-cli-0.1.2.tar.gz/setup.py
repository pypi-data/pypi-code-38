#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re
from setuptools import setup, find_packages


requirements = ["alfa-sdk>=0.1.8", "click>=7.0"]
dev_requirements = ["pytest", "pytest-cov", "black", "pylint", "wb-parameter-handler"]


def get_version():
    root = os.path.dirname(__file__)
    init = open(os.path.join(root, "alfa_cli", "__init__.py")).read()
    regex = re.compile(r"""__version__ = ['"]([0-9.]+(?:a|b|rc)*[0-9]*)['"]""")
    return regex.search(init).group(1)


setup(
    name="alfa-cli",
    version=get_version(),
    description="CLI tools for ALFA",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Widget Brain",
    url="https://bitbucket.org/widgetbrain/alfa-cli",
    packages=find_packages(exclude=["tests*"]),
    package_data={"alfa_cli": []},
    include_package_data=True,
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="cli",
    entry_points={"console_scripts": ["alfa=alfa_cli.cli:main"]},
    scripts=["bin/alfa-complete.sh", "bin/alfa-complete.zsh"],
)
