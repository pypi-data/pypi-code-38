#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from irds import VERSION

setup(
    name='irds',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/irds',
    description='encapsulation of hot-redis features',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=[
        'hot_redis',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/irds/issues',
        'Source': 'https://github.com/coghost/irds',
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['irds', 'izen', 'hot_redis', 'redis', 'ORM'],
)
