#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages
from distutils.core import setup

version = '1.0.4'
with open('README.rst', encoding = "utf-8") as f:
    long_description = f.read()

setup(name='ofxstatement-be-argenta',
      version=version,
      author='Wout Breugelmans',
      author_email='Wout.Breugelmans+ofxstatement@gmail.com',
      url='https://github.com/woutbr/ofxstatement-be-argenta',
      description=('ofxstatement plugin for Argenta'),
      long_description=long_description,
      long_description_content_type='text/x-rst',
      license='MIT',
      keywords=['ofx', 'ofxstatement', 'argenta'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: MIT License',
      ],
      packages=find_packages(),
      namespace_packages=['ofxstatement', 'ofxstatement.plugins'],
      entry_points={
          'ofxstatement': ['argenta = ofxstatement.plugins.argenta:ArgentaPlugin'],
          'console_scripts': ['ofx-argenta-convert = ofxstatement_be_argenta.convert:convert']
      },
      install_requires=[
          'ofxstatement>=0.6.1',
          'openpyxl>=2.6.2',
          'click>=6.7'
      ],
      test_suite='ofxstatement.plugins.tests',
      include_package_data=True,
      zip_safe=True
      )
