# -*- coding: utf-8 -*-

import setuptools
import os

setuptools.setup(
    name="nionutils",
    version="0.3.19",
    author="Nion Software",
    author_email="swift@nion.com",
    description="Nion utility classes.",
    long_description=open("README.rst").read(),
    url="https://github.com/nion-software/nionutils",
    packages=["nion.utils", "nion.utils.test"],
    license='Apache 2.0',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    include_package_data=True,
    test_suite="nion.utils.test",
)
