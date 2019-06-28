# File: setup.py
# Date: 23-Feb-2019
#
# Updates:
#
#
import re

from setuptools import find_packages
from setuptools import setup

packages = []
thisPackage = "rcsb.exdb"

with open("rcsb/exdb/cli/__init__.py", "r") as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("Cannot find version information")

setup(
    name=thisPackage,
    version=version,
    description="RCSB Python ExDB extraction and loading workflows",
    long_description="See:  README.md",
    author="John Westbrook",
    author_email="john.westbrook@rcsb.org",
    url="https://github.com/rcsb/py-rcsb_exdb",
    #
    license="Apache 2.0",
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ),
    entry_points={"console_scripts": ["exdb_exec_cli=rcsb.exdb.cli.ExDbExec:main"]},
    #
    install_requires=[
        "numpy",
        "rcsb.utils.io >= 0.31",
        "rcsb.db >= 0.51",
        "rcsb.utils.config >= 0.18",
        "rcsb.utils.seq >= 0.13",
        "rcsb.utils.ec >= 0.14",
        "rcsb.utils.struct >= 0.17",
        "rcsb.utils.taxonomy >= 0.19",
    ],
    packages=find_packages(exclude=["rcsb.mock-data", "rcsb.exdb.tests-anal", "rcsb.exdb.tests-*", "tests.*"]),
    package_data={
        # If any package contains *.md or *.rst ...  files, include them:
        "": ["*.md", "*.rst", "*.txt", "*.cfg"]
    },
    #
    test_suite="rcsb.exdb.tests",
    tests_require=["tox"],
    #
    # Not configured ...
    extras_require={"dev": ["check-manifest"], "test": ["coverage"]},
    # Added for
    command_options={"build_sphinx": {"project": ("setup.py", thisPackage), "version": ("setup.py", version), "release": ("setup.py", version)}},
    # This setting for namespace package support -
    zip_safe=False,
)
