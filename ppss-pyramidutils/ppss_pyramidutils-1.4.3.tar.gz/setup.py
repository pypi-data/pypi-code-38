#!/usr/bin/env python

#from distutils.core import setup

from setuptools import setup,find_packages

setup(name='ppss_pyramidutils',
      version='1.4.3',
      description='Simple utils to handle data from ini files in Pyramid for python 2.7 & 3',
      author='pdepmcp',
      author_email='pdepmcp@gmail.com',
      install_requires=['six'],
      packages=find_packages()
     )
