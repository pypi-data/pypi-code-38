#!/usr/bin/env python3

from distutils.core import setup

setup(name='pycatj',
      version='0.5.4',
      description='Json/Yaml/Toml Flattener',
      long_description=open('README.md').read(),
      author="Mike 'Fuzzy' Partin",
      author_email='fuzzy@devfu.net',
      maintainer="Mike 'Fuzzy' Partin",
      maintainer_email='fuzzy@devfu.net',
      keywords=['yaml', 'json', 'toml'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3'
      ],
      url='https://git.devfu.net/fuzzy/pycatj/',
      scripts=['pycatj'])
