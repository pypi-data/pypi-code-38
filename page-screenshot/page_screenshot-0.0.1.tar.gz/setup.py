#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@project: take screenshot on a web page
@author: xiaohong
@time: 2019-06-06
@feature: a complete capture from a web page/have a free choose in web page width/
"""

import setuptools
import io

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="page_screenshot",
    version="0.0.1",

    author="xiaohong2019",
    author_email="2229009854@qq.com",

    description="a complete capture from a web page",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/xiaohong2019/page_screenshot",
    packages=setuptools.find_packages(),
    install_requires=[
        'selenium==3.11.0',
        'Pillow',
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
    ],
)
