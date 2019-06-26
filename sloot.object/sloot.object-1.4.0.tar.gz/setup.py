#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from sloot.object import __VERSION__

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="sloot.object",
    version=__VERSION__,
    packages=find_packages(),
    namespace_packages=['sloot'],
    install_requires=[],
    include_package_data=True,
    package_data={'': ['doc/*.rst']},
    platforms='any',
    test_suite=None,
    author="Samuel Jaillet",
    author_email="sam+dev@samjy.com",
    description="Object utils to make life easier",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="MIT",
    keywords=['tools', 'object', 'utils', 'dict'],
    url="https://github.com/samjy/sloot.object",
    download_url="https://github.com/samjy/sloot.object/tarball/%s" % __VERSION__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: Freely Distributable',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
    ],
)

#EOF
