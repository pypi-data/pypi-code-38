#!/usr/bin/env python

import setuptools
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='aio_task_bound_context',
      version='0.2.4',
      description='Context manager that provides a means for context to be '
                  'set, and retrieved in Python AsyncIO.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Ricky Cook',
      author_email='pypi@auto.thatpanda.com',
      url='https://github.com/rickycook/aio_task_bound_context/',
      packages=('aio_task_bound_context',),
      classifiers=(
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
      ),
     )
