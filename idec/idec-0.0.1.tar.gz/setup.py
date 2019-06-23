#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from idec import VERSION

setup(
    name='idec',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tpl', '*.md']},
    author='lihe',
    author_email='imanux@sina.com',
    url='https://github.com/coghost/idec',
    description='run_continuously with schedule',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GPL',
    install_requires=['logzero'],
    project_urls={
        'Bug Reports': 'https://github.com/coghost/idec/issues',
        'Source': 'https://github.com/coghost/idec',
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['idec', 'izen', 'profig', 'logzero'],
)
