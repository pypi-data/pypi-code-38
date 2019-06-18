#!/usr/bin/env python
# coding: utf-8

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='storeimg',
    version='1.8',
    author='noinlj',
    author_email='noinlj@gmail.com',
    url='https://github.com/noinlijin/storeimg',
    description=u'This is a tool which check for compliance iamge is right for Apple Store specifications',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages= setuptools.find_packages(),
    platforms=["all"],
    # install_requires=['Pillow'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'storeimg=storeimg:storeimg',
            'test=storeimg:test'
        ]
    }
)