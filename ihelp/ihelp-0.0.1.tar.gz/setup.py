#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from ihelp import VERSION

setup(
    name='ihelp',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/ihelp',
    description='run_continuously with schedule',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=[

        'psutil', 'wcwidth', 'clint', 'click', 'logzero'],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/ihelp/issues',
        'Source': 'https://github.com/coghost/ihelp',
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['ihelp', 'izen', 'profig', 'logzero'],
)

