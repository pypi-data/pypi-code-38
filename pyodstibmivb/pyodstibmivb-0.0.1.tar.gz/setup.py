from setuptools import setup, find_packages
import os


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pyodstibmivb",
    version='0.0.1',
    author="Emil Vanherp",
    author_email="emil@vanherp.me",
    description="A Python wrapper for the Stib-Mivb opendata API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/EmilV2/pyodstibmivb",
    install_requires=['requests>=2.0'],
    python_requires='>=3',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
