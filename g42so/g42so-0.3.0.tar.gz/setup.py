#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

name = 'g42so'
author = u'Davide Mancusi'
author_email = u'davide.mancusi@cea.fr'

with open('README.md') as readme:
    long_description = readme.read()

setup(name=name,
      author=author,
      author_email=author_email,
      description='A tool to convert Geant4 geometries into shared libraries',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/arekfu/g42so',
      packages=find_packages(),
      package_data={'': ['detector_wrapper.cc.in',
                         'pga_wrapper.cc.in',
                         'version.cc']},
      python_requires='>=2.6, <4',
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      classifiers=[
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
          "Topic :: Scientific/Engineering :: Physics",
          ],
      entry_points={
          'console_scripts': [
              'g42so = g42so.main:main'
              ]
          }
      )
