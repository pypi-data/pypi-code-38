#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages

__author__ = 'ytyng'
__version__ = '0.1.3'
__license__ = 'MIT'

# In [2]: from setuptools.command.bdist_egg import _get_purelib
#
# In [3]: _get_purelib()
# Out[3]: '/Users/yotsuyanagi/.virtualenvs/default/lib/python2.7/site-packages'
# $ cd $(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"

setup(
    name='python-gspreaddict',
    version=__version__,
    description='Google spread sheet as dictionary list. read-only.',
    license=__license__,
    author=__author__,
    author_email='ytyng@live.jp',
    url='https://github.com/ytyng/python-gspreaddict.git',
    keywords='Google spreadsheet, python',
    packages=find_packages(),
    install_requires=['gspread', 'oauth2client'],
    entry_points={},
)
