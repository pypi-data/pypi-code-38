"""Setup script for realpython-reader"""

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="turkce",
    version="0.1.2",
    description="TurkceAI",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/turkceAI/python",
    author="TurkceAI",
    author_email="ttarikkucuk@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["reader"],
    entry_points={"console_scripts": ["realpython=reader.__main__:main"]},
)
