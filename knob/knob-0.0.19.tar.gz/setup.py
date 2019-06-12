# -*- coding:utf-8 -*-

import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()


setuptools.setup(
    name="knob",
    version="0.0.19",
    author="claydodo and his little friends (xiao huo ban)",
    author_email="claydodo@foxmail.com",
    description="Django utils collection",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/claydodo/knob",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7 ",
        "Programming Language :: Python :: 3 ",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'six',
        'pycrypto >= 2.0',
        'krux',
        'krust',
    ]
)
