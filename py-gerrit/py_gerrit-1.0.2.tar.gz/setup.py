# -*- coding: utf8 -*-
"""
__author__ = 'Yan' Started by '2019/6/17'
"""

from setuptools import setup, find_packages

setup(
    name='py_gerrit',
    version='1.0.2',
    description='gerrit简单封装',
    long_description='简单封装gerrit ssh-commands，后续进一步封装rest api方法',
    keywords='gerrit tools',
    install_requires=[
        'requests',
    ],
    packages=find_packages(),
    author='allen.you',
    author_email='youyan0704@163.com',
    url='https://github.com/youyan0704/py_gerrit',
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ]
)
