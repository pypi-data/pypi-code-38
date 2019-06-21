#!/usr/bin/env python
# -*- coding:utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.2.0'

setup(
    name='zctestpy',
    version=version,
    description='X-ABT Nanopore Assembly Pipeline',
    # long_description=readme,
    packages=['zcpy'],
    # install_requires=[
    #     'PyYAML==3.11',
    #     'requests==2.5.3'
    # ],
    entry_points={
        'console_scripts': [
            'zctestpy = zcpy.main:main',
        ]
    },
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ]
)