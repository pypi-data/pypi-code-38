#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from amq import VERSION

setup(
    name='iamq',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/iamq',
    description='encapsulation of mqtt features',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=[
        'logzero',
        'paho-mqtt',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/iamq/issues',
        'Source': 'https://github.com/coghost/iamq',
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['iamq', 'izen', 'profig', 'logzero'],
)
