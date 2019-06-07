import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dftogsheet",
    version="0.0.2",
    author="William Dry",
    author_email="wpbdry@gmail.com",
    description="A Python module for writing pandas DataFrame objects directly to Google Spreadsheets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wpbdry/gsheets_pkg",
    packages=setuptools.find_packages(where="./dftogsheet/*"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)