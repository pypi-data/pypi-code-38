import pathlib
from setuptools import setup
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "wrappers/README.rst").read_text()

# This call to setup() does all the work
setup(
    name="python-mano-wrappers",
    version="0.9.8",
    description="REST API Wrappers for various MANOs in compliance with ETSI SOL0005",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/CN-UPB/pg-scrambLe",
    author="PG-SCrAMbLE Team WP3",
    author_email="ashwin@campus.uni-paderborn.de",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["tests"]),
    install_requires=["requests"],
)