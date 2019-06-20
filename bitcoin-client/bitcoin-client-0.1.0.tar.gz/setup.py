#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='bitcoin-client',
    version='0.1.0',
    description='bitcoin python client',
    long_description_markdown_filename='README.md',
    author='Dmitry Zhidkih',
    author_email='zhidkih.dmitry@gmail.com',
    url='https://github.com/dmitry1981/bitcoin-client',
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    # setup_requires=['setuptools-markdown'],
    python_requires='>=3.6,<4',
    extras_require={},
    py_modules=['bitcoin_block_book', ],
    license="MIT",
    zip_safe=False,
    keywords='bitcoin blockbook',
    packages=find_packages(exclude=['docs', 'tests']),
)
