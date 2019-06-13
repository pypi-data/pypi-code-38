#!/usr/bin/env python

"""Johnnyruzdev fork of the Kegberry Package

Kegberry turns a Raspberry Pi into a keg monitor and digital taplist.

Kegberry is based on Kegbot, and makes it easy to install and run a
full keg monitoring solution on Raspberry Pi.  For more information, see the
project home page at kegberry.com.

Originally forked from version 2.1.1
"""

from setuptools import setup, find_packages

VERSION = '0.0.6'
DOCLINES = __doc__.split('\n')

SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])
DEPENDENCIES = [
  'python-gflags',
]

def setup_package():
  setup(
      name = 'jrfork-kegberry',
      version = VERSION,
      description = SHORT_DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      author = 'johnnyruzdev',
      author_email = 'johnnyruzdev01@outlook.com',
      url = 'http://kegberry.kegbot.org/',
      packages = find_packages(),
      scripts = [
        'bin/kegberry',
      ],
      install_requires = DEPENDENCIES,
      include_package_data = True,
  )

if __name__ == '__main__':
  setup_package()
