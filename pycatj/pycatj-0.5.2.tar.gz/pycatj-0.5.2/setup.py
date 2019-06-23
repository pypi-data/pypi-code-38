#!/usr/bin/env python3

from distutils.core import setup

setup(name='pycatj',
      version='0.5.2',
      description='Json/Yaml Flattener',
      long_description='''A JSON/YAML flattener that displays the paths for each element in an easy
to ready, colorized format on your console. Think `jq` but with a flattened structure instaed of the
full nested monty.''',
      author="Mike 'Fuzzy' Partin",
      author_email='fuzzy@devfu.net',
      maintainer="Mike 'Fuzzy' Partin",
      maintainer_email='fuzzy@devfu.net',
      keywords=['yaml', 'json'],
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
