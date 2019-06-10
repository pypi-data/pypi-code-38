#!/usr/bin/env python
# coding=utf-8
# reference : https://www.jianshu.com/p/e9ec8666decc
# flow:
#   1. python setup.py sdist build
#   2. python setup.py bdist_wheel upload (deprecated)
#   2. or twine upload dist/* (pip install twine)
# install:
# pip install zac-pyutils  --upgrade -i https://pypi.python.org/pypi
from setuptools import setup, find_packages

setup(
    name='zac_pyutils',
    version='1.53',
    description=(
        'collection of some useful functions'
    ),
    long_description=open('README.rst').read(),
    author='zach',
    author_email='2achx0121@gmail.com',
    maintainer='zach',
    maintainer_email='2achx0121@gmail.com',
    license='BSD License',
    packages=['zac_pyutils'],
    platforms=["all"],
    url='https://github.com/Zachary4biz/ExqUtils',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
