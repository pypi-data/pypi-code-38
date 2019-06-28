#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages
from tlclient.trader import __version__

setup(
    name='tlclient',
    version=__version__,
    description=(
        'strategy side SDK for traders.link'
    ),
    long_description=open('README.rst').read(),
    author='puyuan.tech',
    author_email='info@puyuan.tech',
    maintainer='puyuan_staff',
    maintainer_email='github@puyuan.tech',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='http://www.puyuan.tech',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'pytz >= 2019.1',
        'pyzmq >= 18.0.0',
    ]
)