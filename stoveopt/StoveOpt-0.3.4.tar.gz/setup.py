# -*- coding: utf-8 -*-
"""
Created on Thu May  9 15:34:23 2019

@author: Lee
"""
import setuptools
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
      name='StoveOpt',
      version='0.3.4',
      description='Biomass cookstove optimization package',
      author='Liam Cassidy',
	  url='https://github.com/Liam-Cassidy/StoveOpt',
      author_email='cassidyl@oregonstate.edu',
      classifiers=[
              'License :: OSI Approved :: BSD License',
              'Natural Language :: English',
              'Programming Language :: Python',
      ],
      
      license='MIT',
      python_requires='>=2.7',
      zip_safe=False,
      packages=setuptools.find_packages(),
      
	  package_dir={'StoveOpt': 'StoveOpt',
	  },
	  include_package_data=True,		
      )
      
