#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from icraw import VERSION

setup(
    name='icraw',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/icraw',
    description='run_continuously with schedule',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=[
        'tqdm', 'requests', 'beautifulsoup4', 'logzero', 'ihelp'
    ],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/icraw/issues',
        'Source': 'https://github.com/coghost/icraw',
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['icraw', 'izen', 'profig', 'logzero'],
)
