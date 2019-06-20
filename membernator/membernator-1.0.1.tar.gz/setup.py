#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Setup"""
from membernator import __version__
from setuptools import setup

setup(
    name='membernator',
    version=__version__,
    description="""A tool that can be used to scan membership cards and
                   establish if they're valid or not against a CSV database.""",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Louis-Philippe Véronneau',
    python_requires='>=3.5.0',
    url='https://gitlab.com/baldurmen/membernator',
    install_requires=['docopt', 'pygame'],
    py_modules=['membernator'],
    entry_points={
        'console_scripts': [
            'membernator = membernator:main',
        ]
    },
    license='ISC',
    classifiers=[
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
    ],
)
