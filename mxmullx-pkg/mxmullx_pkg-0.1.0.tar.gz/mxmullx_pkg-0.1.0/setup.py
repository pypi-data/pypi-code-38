
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "mxmullx_pkg",
    version = "0.1.0",
    author = "Xian Lian",
    author_email = "xianl828@163.com",
    description = "An example for teaching how to publish a Python package",
    long_description = long_description,
    long_description_content_types = "text/markdown",
    url = "http://github.com/pypa/sampleproject",
    package = setuptools.find_packages(),
    classfiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operation System :: OS Independent"
    ],

)