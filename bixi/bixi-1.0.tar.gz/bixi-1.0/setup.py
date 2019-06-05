#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup


INSTALL_REQUIRES = [
    'uvloop',
    'mode',
    'click',
    'croniter',
    'asyncpg'
]

setup(
    name='bixi',
    version='1.0',
    author='Mousse',
    author_email='zibuyu1995@gmail.com',
    url='https://github.com/zibuyu1995/Bixi',
    description='Asynchronous Task Queue',
    long_description=open("README.rst").read(),
    platforms=['any'],
    license='MIT',
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.6.0',
    keywords=[
        'asynchronous',
        'task',
        'queue'
    ],
    entry_points={
        'console_scripts': [
            'bixi = bixi.cli:start',
        ],
    },
)
