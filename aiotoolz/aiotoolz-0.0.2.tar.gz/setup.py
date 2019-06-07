#!/usr/bin/env python

from os.path import exists
from setuptools import setup
import aiotoolz

setup(name='aiotoolz',
      version=aiotoolz.__version__,
      description='List processing tools and functional utilities '
                  '(Ported to support async/await)',
      url='https://github.com/eabrouwer3/aiotoolz/',
      author='https://raw.github.com/eabrouwer3/aiotoolz/master/AUTHORS.md',
      maintainer='Ethan Brouwer',
      maintainer_email='eabrouwer3@gmail.com',
      license='BSD',
      keywords='functional utility itertools functools',
      packages=['aiotoolz',
                'aiotoolz.sandbox',
                'aiotoolz.curried',
                'aiotlz'],
      package_data={'aiotoolz': ['tests/*.py']},
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      zip_safe=False,
      python_requires=">=3.5",
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7"])

# "Programming Language :: Python :: Implementation :: CPython",
# "Programming Language :: Python :: Implementation :: PyPy"
