#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
from setuptools import setup, find_packages


README_PATH = os.path.join(os.path.dirname(__file__), 'readme.org')
VERSION_PATH = os.path.join(os.path.dirname(__file__), 'pygass', 'version.py')
version = {}
with open(VERSION_PATH) as fp:
    exec(fp.read(), version)
long_desc = open(README_PATH).read() + '\n\n'

setup(name='pygass',
      version=version['__version__'],
      license='GPL-3',
      author='Oliver Marks',
      author_email='oly@digitaloctave.com',
      url='https://gitlab.com/python-open-source-library-collection/pygass',
      description='Server side implementation of Google Analytics in Python.',
      long_description=long_desc,
      long_description_content_type="text/plain",
      keywords='google analytics server side',
      requires=['requests'],
      setup_requires=['pytest-runner==4.4'],
      install_requires=['setuptools'],
      data_files=[("readme.org", ['readme.org'])],
      packages=find_packages(),
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Web Environment',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
      ],
      test_suite='tests',
      tests_require=['mock', 'pytest']
    )
