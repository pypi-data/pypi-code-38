# -*- coding: utf-8 -*-
"""
Created on Thu May  9 15:34:23 2019

@author: Lee
"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
      name='StoveOpt',
      version='0.1.0',
      description='Biomass cookstove optimization package',
      author='Liam Cassidy',
      author_email='cassidyl@oregonstate.edu',
      classifiers=[
              'License :: OSI Approved :: BSD License',
              'Natural Language :: English',
              'Programming Language :: Python',
      ],
      
      license='MIT',
      python_requires='>3',
      zip_safe=False,
      packages=find_packages(),
      package_dir={'StoveOpt': 'StoveOpt',
                   'StoveOpt.tests': 'StoveOpt/tests'},
      include_package_data=True
      )
      
