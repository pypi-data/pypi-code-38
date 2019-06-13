#!/usr/bin/env python
#-*- encoding:utf-8 -*-
# coding=utf-8

from setuptools import setup, find_packages
from xyscript.config import Config
import os

__author__ = 'XYCoder'
__date__ = '2019/04/18'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    extra = {'scripts': ["bin/xyscript"]}
else:
    extra = {
        'test_suite': 'xyscript.test',
        'entry_points': {
            'console_scripts': ['xyscript = xyscript.api:main'],
        },
    }

data_files = [('/xyscript',['config.ini'])]

setup(
    name='xyscript',
    version=Config().get_version(),
    description=Config().get_description(),
    long_description=Config().get_long_desctription(),
    author='XYCoder',
    author_email='m18221031340@163.com',
    maintainer='XYCoder',
    maintainer_email='m18221031340@163.com',
    license='BSD License',
    packages=find_packages(),
    # data_files=data_files,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    platforms=["all"],
    url='https://gitlab.saicmobility.com/saic-framework-ios/xyscript',
    install_requires=['requests', 'GitPython', 'setuptools','configparser'],
    include_package_data=True,
    classifiers=[
        "Development Status :: 6 - Mature",
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Software Development :: Libraries'
    ],
**extra)

if __name__ == "__main__":
    pass
    # Config().get_description()
    # print(setup)