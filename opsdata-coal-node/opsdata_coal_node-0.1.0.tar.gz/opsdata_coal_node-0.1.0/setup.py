"""
The setup script for the dataset.
"""
import sys
from pathlib import Path

from setuptools import setup, find_packages

# make sure python 3 is running
if sys.version_info.major < 3:
    raise Exception(f"Obsplus datasets cannot be run on python 2")


def get_package_data_files():
    """ Create a list of datafiles """
    data_path = Path("opsdata_coal_node") / "data"
    return [("", list(data_path.rglob()))]


# get requirements
requirements = open("requirements.txt")
test_requirements = open("tests/requirements.txt")

license_classifiers = {"BSD license": "License :: OSI Approved :: BSD License"}

setup(
    author="Derrick Chambers",
    author_email="djachambeador@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="A dataset collected over an operating longwall coalmine using a dense network of geophones",
    long_description=open("README.md").read(),
    entry_points={"obsplus.datasets": ["coal_node=opsdata_coal_node.core"]},
    install_requires=requirements,
    license="BSD",
    include_package_data=True,
    name="opsdata_coal_node",
    packages=find_packages(include=["ops_datasetcoal_node"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/d-chambers/coal_node",
    version="0.1.0",
    zip_safe=False,
)
