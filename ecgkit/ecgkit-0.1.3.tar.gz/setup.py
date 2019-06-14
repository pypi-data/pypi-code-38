#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(name='ecgkit',
      version='0.1.3',
      keywords=['ECG','preprocess','plot'],
      description='ECG Toolkits',
      long_description='Toolkits for ECG Analysis in Python',
      license='MIT Licence',
      packages=find_packages(),
      package_dir={'ecgkit': 'ecgkit'},
      author='dingzj',
      author_email='dingzj@mail.tsinghua.edu.cn',

      include_package_data = True,
      platforms='any',
      install_requires=['matplotlib', 'numpy', 'scipy', 'wfdb', 'pywavelets', 'peakutils'],
      url="https://github.com/SergejTHU/ecgkit"
)

