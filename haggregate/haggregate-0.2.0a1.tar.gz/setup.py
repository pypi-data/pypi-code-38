#!/usr/bin/env python
"""

We don't isort this file because Cython has to go after setuptools.
isort:skip_file
"""

# Running setup.py requires having installed numpy and Cython. There are some
# complicated solutions that might make it possible to somehow add them to
# "setup_requirements" etc., but I decided they aren't worth it. We'd better wait until
# Python has better packaging tools (this shouldn't need more than 100 more years).
# More information on the complicated solutions:
# https://stackoverflow.com/questions/37471313/
# https://stackoverflow.com/questions/14657375/
# https://stackoverflow.com/questions/2379898/

import os
import re

import numpy
from setuptools import find_packages, setup
from Cython.Build import cythonize

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Click>=7.0,<8", "htimeseries>=1.1,<2"]

setup_requirements = ["cython>=0.29,<0.30"]

test_requirements = []


def get_version():
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    init_py_path = os.path.join(scriptdir, "haggregate", "__init__.py")
    with open(init_py_path) as f:
        return re.search(r'^__version__ = "(.*?)"$', f.read(), re.MULTILINE).group(1)


setup(
    ext_modules=cythonize(["haggregate/regularize.pyx"]),
    include_dirs=[numpy.get_include()],
    author="Antonis Christofides",
    author_email="antonis@antonischristofides.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    description="Aggregates htimeseries to larger steps",
    entry_points={"console_scripts": ["haggregate=haggregate.cli:main"]},
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="haggregate",
    name="haggregate",
    packages=find_packages(include=["haggregate"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/openmeteo/haggregate",
    version=get_version(),
    zip_safe=False,
)
