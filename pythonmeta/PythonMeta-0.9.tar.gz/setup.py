#!/usr/bin/env python
# coding=utf-8
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PythonMeta",
    version="0.9",
    author="Deng Hongyong",
    author_email="dephew@126.com",
    keywords=["meta analysis", "meta-analysis", "meta_analysis", "systematic review", "EBM", "Evidence-based Medicine"],
    description="A Python module of Meta-Analysis, usually applied in systemtic reviews of Evidence-based Medicine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.pymeta.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    install_requires=["matplotlib"] 
)