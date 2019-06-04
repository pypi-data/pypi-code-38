#!/usr/bin/env python3

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='stormbot-role',
      version='2.0b1',
      description='role plugin for stormbot',
      long_description=long_description,
      author='Paul Fariello',
      author_email='paul@fariello.eu',
      url='https://github.com/manoir/stormbot-role',
      packages=find_packages(),
      install_requires=['stormbot>=2.0b1', 'isodate'],
      entry_points={'stormbot.plugins': ['role = stormbot_role:VolunteerPicker']},
      classifiers=['Environment :: Console',
                   'Operating System :: POSIX',
                   'Topic :: Communications :: Chat',
                   'Programming Language :: Python'])
