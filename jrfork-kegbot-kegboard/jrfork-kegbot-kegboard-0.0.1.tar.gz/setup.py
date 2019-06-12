#!/usr/bin/env python
"""Johnnyruzdev Fork of the Kegboard support library.

This package contains the Python protocol support for Kegboard.  For more
information on Kegboard, see http://kegbot.org/kegboard/

Initially Forked from version 1.1.5 of the Kegboard library
"""

DOCLINES = __doc__.split('\n')

# Change this to True to include optional dependencies
USE_OPTIONAL = False

VERSION = '0.0.1'
SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])

def setup_package():
  from setuptools import setup, find_packages

  setup(
      name = 'jrfork-kegbot-kegboard',
      version = VERSION,
      description = SHORT_DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      author = 'johnnyruzdev',
      author_email = 'johnnyruzdev01@outlook.com',
      url = 'http://kegbot.org/',
      packages = find_packages(exclude=['testdata']),
      namespace_packages = ['kegbot'],
      scripts = [
        'distribute_setup.py',
        'bin/kegboard-monitor.py',
        'bin/kegboard-tester.py',
        'bin/kegboard-info.py',
        'bin/set-kegboard-serialnumber',
      ],
      install_requires = [
        'kegbot-pyutils >= 0.1.2',
        'python-gflags',
        'pyserial',
      ],
      include_package_data = True,
  )

if __name__ == '__main__':
  setup_package()
