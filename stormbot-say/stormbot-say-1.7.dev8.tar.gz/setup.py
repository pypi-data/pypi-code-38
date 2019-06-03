#!/usr/bin/env python3

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='stormbot-say',
      version='1.7.dev8',
      description='text to speech plugin for stormbot',
      long_description=long_description,
      author='Paul Fariello',
      author_email='paul@fariello.eu',
      url='https://github.com/manoir/stormbot-say',
      packages=find_packages(),
      install_requires=['stormbot>=1.7.dev7', 'gtts'],
      entry_points={'stormbot.plugins': ['say = stormbot_say:Say']},
      classifiers=['Environment :: Console',
                   'Operating System :: POSIX',
                   'Topic :: Communications :: Chat',
                   'Programming Language :: Python'])
