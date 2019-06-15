#!/usr/bin/env python

"""
Simple setup - should work on most Python versions.
"""

import setuptools

with open("README.md", "r") as fh:
    # pylint: disable=invalid-name
    long_description = fh.read()

setuptools.setup(
    name='mitoc_const',
    version='0.4.1',
    author='David Cain',
    author_email='davidjosephcain@gmail.com',
    url='https://github.com/DavidCain/mitoc-const',
    packages=['mitoc_const'],
    description='Constants for use across MIT Outing Club infrastructure',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
)
