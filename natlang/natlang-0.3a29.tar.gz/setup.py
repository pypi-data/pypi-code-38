# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Setup
# Simon Fraser University
# Jetic Gu
#
import setuptools
from distutils.util import convert_path

# Get version
main_ns = {}
ver_path = convert_path('natlang/__version__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="natlang",
    version=main_ns['version'],
    author="Jetic Gū, Rory Wang",
    author_email="jeticg@sfu.ca",
    description="Natural language data loading tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeticg/datatool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'jieba',
        'progressbar',
        'six',
        'astor',
        'bashlex',
    ],
    test_suite='natlang.testSuite'
)
