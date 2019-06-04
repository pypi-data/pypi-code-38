#!/usr/bin/env python3

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='stormbot-fortune',
      version='2.0b1',
      description='fortune plugin for stormbot',
      long_description=long_description,
      author='Paul Fariello',
      author_email='paul@fariello.eu',
      url='https://github.com/manoir/stormbot-fortune',
      packages=find_packages(),
      package_data={'stormbot_fortune': ['data/*.dic']},
      install_requires=['stormbot>=2.0b1'],
      entry_points={'stormbot.plugins': ['fortune = stormbot_fortune:Fortune']},
      classifiers=['Environment :: Console',
                   'Operating System :: POSIX',
                   'Topic :: Communications :: Chat',
                   'Programming Language :: Python'])
