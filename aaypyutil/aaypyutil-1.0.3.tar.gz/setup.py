"""Setup script for aaypyutil"""

import os.path

from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="aaypyutil",
    version="1.0.3",
    description="Common python util functions",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/aayushuppal/aaypyutil",
    author="Aayush Uppal",
    author_email="aayuppal@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["aaypyutil"],
    include_package_data=True,
    install_requires=[],
    entry_points={},
)
