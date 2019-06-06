"""Setup script for kesh-utils"""

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="kesh-utils",
    version="0.3.1",
    description="Kesh Utils for Data science/EDA/Data preparation ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/KeshavShetty/ds",
    author="Keshav Shetty",
    author_email="keshavshetty@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["KUtils/common", "KUtils/eda", "KUtils/linear_regression"],
    include_package_data=True,
)
