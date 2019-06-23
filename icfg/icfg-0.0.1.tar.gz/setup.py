#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from cfg.__const__ import VERSION

setup(
    name='icfg',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/icfg',
    description='encapsulation of profig and logzero',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=[
        'logzero',
        'profig',
        'psutil',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/icfg/issues',
        'Source': 'https://github.com/coghost/icfg',
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['icfg', 'izen', 'profig', 'logzero'],
)
