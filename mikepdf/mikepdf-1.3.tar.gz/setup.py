
import setuptools
from pathlib import Path


setuptools.setup(
    name="mikepdf",
    version=1.3,
    long_description="Long Description",
    packages=setuptools.find_packages(
        exclude=["tests", "data"]))
