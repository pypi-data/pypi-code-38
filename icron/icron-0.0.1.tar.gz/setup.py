#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from icron import VERSION

setup(
    name='icron',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/icron',
    description='run_continuously with schedule',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=[],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/icron/issues',
        'Source': 'https://github.com/coghost/icron',
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['icron', 'izen', 'profig', 'logzero'],
)
