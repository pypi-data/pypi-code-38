"""Setup script for itime"""

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="itime",
    version="0.0.1",
    description="awesome converter for various time formata",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/slxiao/itime",
    author="Shelwin Xiao",
    author_email="shliangxiao@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["itime"],
    include_package_data=True,
    install_requires=[
        "pytz", "calendar"
    ]
)
