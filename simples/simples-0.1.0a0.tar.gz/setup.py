import os.path
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="simples",
    version="v0.1.0-alpha",
    description="Soma dois números.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jecamanga/simples",
    author="jeca",
    author_email="nyanvamp@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    include_package_data=True
)