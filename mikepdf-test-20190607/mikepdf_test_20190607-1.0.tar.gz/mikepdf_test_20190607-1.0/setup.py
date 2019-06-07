import setuptools
from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mikepdf_test_20190607",
    version=1.0,
    long_description=long_description,
    packages=setuptools.find_packages(exclude=["tests", "data"])

)
