#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='tad4bj',
      version='2.0.dev1',
      description='Tabular Annotations of Data for Batch Jobs',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Alex Barcelo',
      author_email='alex@betarho.net',
      url='https://github.com/alexbarcelo/tad4bj',
      packages=['tad4bj'],
      extras_require={
          'yaml': ["pyyaml"],
      },
      entry_points={
          'console_scripts': {'tad4bj = tad4bj:main'},
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Database',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: System :: Logging',
      ],
      )

