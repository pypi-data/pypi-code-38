#!/usr/bin/env python

from setuptools import setup, find_packages

from Kittens import __version__

setup(name='astro-kittens',
      version=__version__,
      description='Collection of Python utility functions for purr, tigger, meqtrees and others',
      author='Oleg Smirnov',
      author_email='Oleg Smirnov <osmirnov@gmail.com>',
      url='https://github.com/ska-sa/kittens',
      packages=find_packages(),
      install_requires=['configparser', 'astropy'],
     )

