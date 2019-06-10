#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

read_md = lambda f: open(f, 'r').read()

setup(name='urecon',
      version='0.1.1',
      description='Find usernames across over 70 social networks',
      long_description=read_md('README.md'),
      long_description_content_type='text/markdown',
      url='https://github.com/s4w3d0ff/userrecon',
      author='s4w3d0ff',
      license='GPL v3',
      packages=['urecon'],
      install_requires=['requests', 'beautifulsoup4'],
      zip_safe=False,
      scripts=['bin/userrecon'],
      keywords=['username', 'socialmedia', 'social', 'media', 'network', 'account'],
      classifiers = [
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 2'
            ]
      )
