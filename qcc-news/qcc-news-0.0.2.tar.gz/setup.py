#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

ver = '0.0.2'

setup(
    name='qcc-news',
    version=ver,
    description=(
        'All like QCC news manage business can from qcc-news. Web-mother include member manage, '
        'organization manage, and catalog manage. Especially qcc-news support authorization management.'
    ),
    long_description='Docs for this project are maintained at https://gitee.com/qcc100/qcc-news.git.',
    author='Yang Chunbo',
    author_email='ycb@microto.com',
    maintainer='Yang Chunbo',
    maintainer_email='ycb@microto.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://gitee.com/qcc100/qcc-news.git',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
    ]
)
