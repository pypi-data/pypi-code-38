"""setup.py for rdutils python package
"""

import setuptools

__version__ = '0.1'
__author__ = 'Rob Dupre (VCA Technology)'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='rdutils',
    version='0.3',
    author="Rob Dupre",
    author_email="robdupre@gmail.com",
    description="A set of python helper utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/robdupre/rdutils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)