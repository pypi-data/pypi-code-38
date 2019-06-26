#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import sys

try:
  from setuptools import setup
except:
  from distutils.core import setup

import ktk


if sys.version_info < (2, 5):
  sys.exit('Python 2.5 or greater is required.')

with open('README.md') as fp:
  readme = fp.read()
  print(type(readme))

def split_path(path, result=None):
  if result is None:
    result = []
  head, tail = os.path.split(path)
  if head == '':
    return [tail] + result
  if head == path:
    return result
  return split_path(head, [tail] + result)

def find_packages():
  packages = []
  repo_root_dir = os.path.dirname(__file__)
  if repo_root_dir != '':
    os.chdir(repo_root_dir)
  src_root_dir = 'ktk'
  for dirpath, dirnames, filenames in os.walk(src_root_dir):
    if os.path.basename(dirpath).startswith("."):
      continue
    if '__init__.py' in filenames:
      packages.append('.'.join(split_path(dirpath)))
  return packages

packages = find_packages()
version = "0.0.2"
license = "MIT"
project_name = "ktk-python"
 
setup(
    name=project_name,
    version=version,
    description='kmiku7\'s tookkit for Python',
    long_description=readme,
    author='kmiku7',
    author_email='kakoimiku@gmail.com',
    license=license,
    packages=packages,
    platforms=["all"],
    url='https://github.com/kmiku7/ktk-python', 
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)