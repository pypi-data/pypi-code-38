#!/usr/bin/env python3

import sys
import numpy

if sys.version_info[0] < 3:
    sys.exit('Sorry, Python < 3.x is not supported')

# Try using setuptools first, if it's installed
from setuptools import setup, find_packages
from setuptools.extension import Extension

# Need to add all dependencies to setup as we go!
setup(name='library_simulator',
      packages=find_packages(),
      version='0.1',
      description="Python software package for simulating random mutagenesis experiments",
      long_description=open("README.rst").read(),
      author='Michael J. Harms',
      author_email='harmsm@gmail.com',
      url='https://github.com/harmslab/library_simulator',
      download_url='https://github.com/harmslab/library_simulator/archive/v0.1.tar.gz',
      zip_safe=False,
      install_requires=["matplotlib","scipy","numpy"],
      classifiers=['Programming Language :: Python'],
      package_data={'': ['library_simulator/mutation_spectra/*.csv']},
      include_package_data=True)
