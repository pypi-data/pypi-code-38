#!/usr/bin/env python

import sys

import os
import re
from glob import glob
from setuptools import setup, find_packages

from ucca.__version__ import VERSION

try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
os.chdir(os.path.dirname(os.path.abspath(this_file)))

extras_require = {}
install_requires = []
for requirements_file in glob("requirements.*txt"):
    suffix = re.match(r"[^.]*\.(.*)\.?txt", requirements_file).group(1).rstrip(".")
    with open(requirements_file) as f:
        (extras_require.setdefault(suffix, []) if suffix else install_requires).extend(f.read().splitlines())

try:
    import pypandoc
    try:
        pypandoc.convert_file("README.md", "rst", outputfile="README.rst")
    except (IOError, ImportError, RuntimeError):
        pass
    long_description = pypandoc.convert_file("README.md", "rst")
except (IOError, ImportError, RuntimeError):
    long_description = ""


setup(name="UCCA",
      version=VERSION,
      install_requires=install_requires,
      extras_require=extras_require,
      description="Universal Conceptual Cognitive Annotation",
      long_description=long_description,
      author="Daniel Hershcovich",
      author_email="danielh@cs.huji.ac.il",
      url="https://github.com/huji-nlp/ucca",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "Programming Language :: Python :: 3.6",
          "Topic :: Text Processing :: Linguistic",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
      ],
      packages=find_packages(),
      )
