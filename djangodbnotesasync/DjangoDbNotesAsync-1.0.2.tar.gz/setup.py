# coding: utf-8

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DjangoDbNotesAsync",
    version="1.0.2",
    author="yirantai",
    author_email="896275756@qq.com",
    description="a package for adding django model notes and field help_text to mysql table comment and field comment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yirantai-Angle/DjangoDbNotesAsync",
    packages=setuptools.find_packages(),
    classifiers=[
            "Programming Language :: Python :: 3.6",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
)