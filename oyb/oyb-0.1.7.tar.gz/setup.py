"""Forwards call to setuptools.setup() after parsing:
   * name from package folder
   * long description from README.rst
   * packages from setuptools.find_packages()
   * dependencies from requirements.txt
   * remaining properties from package-level package.json
"""

import setuptools

with open("README.rst", 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="oyb",
    version="0.1.7",
    author="Brian Kirkpatrick",
    author_email="code@tythos.net",
    description="Oy vey! So many orbit models. Here's another one.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/Tythos/oyb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
