#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='DroneSim',
    version=0.1,
    description=(
        'Yet Another Python API for SJTU Drone Contest.'
    ),
    author='DUT Drone Lab',
    maintainer='Yuan Yichen',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    classifiers=[
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'msgpack-rpc-python',
        'numpy',
    ],
)
