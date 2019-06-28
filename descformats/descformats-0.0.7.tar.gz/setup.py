#!/usr/bin/env python
"""
Lightweight pipeline engine for LSST DESC
Copyright (c) 2018 LSST DESC
http://opensource.org/licenses/MIT
"""
from setuptools import setup

setup(
    name='descformats',
    version='0.0.7',
    description='Interface wrappers to file types in DESC pipelines',
    url='https://github.com/LSSTDESC/DESCFormats',
    maintainer='Joe Zuntz',
    license='MIT',
    python_requires='>=3',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['descformats', 'descformats.tx', 'descformats.pz'],
)
