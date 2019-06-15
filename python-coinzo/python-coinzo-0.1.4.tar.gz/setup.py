#!/usr/bin/env python
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-coinzo",
    version="0.1.4",
    author="tolgamorf",
    author_email="cryptolga@gmail.com",
    description="coinzo REST API python implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tolgamorf/python-coinzo",
    packages=["coinzo"],  # setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="coinzo exchange rest api bitcoin ethereum btc eth neo eos xrp hot try",
)
