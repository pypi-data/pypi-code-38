#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="sepp",
    version="0.0.0",
    description="Science Exploitation and Preservation Platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="SEPP Development Consortium",
    author_email="dmb@uninova.pt",
    url="https://repos.cosmos.esa.int/socci/projects/SEPP/repos/sepp",
    license="Proprietary",  # actually to be determined
    packages=["sepp"],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.7'
    )
)
