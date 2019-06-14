# -*- coding: utf-8 -*-
# Copyright 2018 Mobicage NV
# NOTICE: THIS FILE HAS BEEN MODIFIED BY MOBICAGE NV IN ACCORDANCE WITH THE APACHE LICENSE VERSION 2.0
# Copyright 2018 GIG Technology NV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @@license_version:1.5@@

# !/usr/bin/env python

import os

import mcfw

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def path(p):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), p)


requirements = []
tests_requirements = requirements + []

setup(name='mcfw',
      version=mcfw.__version__,
      description='Framework for easy caching and rest api calls in google appengine projects',
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
      ],
      keywords=['mcfw', 'appengine', 'rest', 'cache'],
      author='Green IT Globe',
      author_email='apps@greenitglobe.com',
      url='https://github.com/rogerthat-platform/mcfw',
      license='Apache 2.0',
      packages=['mcfw'],
      install_requires=requirements,
      tests_require=tests_requirements,
      )
