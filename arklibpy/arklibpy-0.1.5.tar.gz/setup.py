#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='arklibpy',
    version='0.1.5',
    author='Fangzhou Wang',
    author_email='fwangusc@gmail.com',
    license='MIT',
    keywords='Database',
    long_description=open(path.join(here, 'README.md'), encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fangzhouwang/arklibpy',
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6, !=3.5.*, <4',
    packages=find_packages(exclude=['unit_tests']),
    requires=[
        '_mysql',
    ],
    test_suite='unit_tests'
)
