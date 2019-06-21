"""
setup.py contains the basic PyPi setup info
"""

import pathlib
from setuptools import setup, find_packages

CUR_DIR = pathlib.Path(__file__).parent
README = (CUR_DIR / "README.md").read_text()

setup(
    name="jilkpw_py",
    version="1.0.4",
    description="Jilk.pw Python Wrapper is a small python module for connecting to Jilk.pw's Public API. This can help if you would like to embed items from your Discord Server into anything that binds with Python.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/scOwez/jilkpw-python-wrapper",
    author="scOwez",
    author_email="owez@scalist.net",
    license="Apache",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
)