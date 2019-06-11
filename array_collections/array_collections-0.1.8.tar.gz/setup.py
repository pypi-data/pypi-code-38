# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 16:42:49 2018

This module includes classes and functions relating arrays.

@author: Guest Group
"""
from setuptools import setup

setup(
      name = 'array_collections',
      packages = ['array_collections'],
      license='MIT',
      version = '0.1.8',
      description = 'A collection of numpy ndarray subclasses.',
      long_description=open('README.rst').read(),
      author = 'Yoel Cortes-Pena',
      install_requires=['numpy', 'pandas', 'free_properties'],
      package_data = {'array_collections': []},
      platforms=["Windows"],
      author_email = 'yoelcortes@gmail.com',
      url = 'https://github.com/yoelcortes/array_collections',
      download_url = 'https://github.com/yoelcortes/array_collections.git'
      )
      

