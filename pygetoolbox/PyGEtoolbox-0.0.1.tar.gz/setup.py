# -*- coding: utf-8 -*-

from setuptools import setup
import os
import sys

with open('README.md') as f:
    readme = f.read()

setup(
    name='PyGEtoolbox',
    version='0.0.1',
    description='Gene expression toolbox in Python', 
    long_description_content_type="text/markdown",
    long_description=readme,
    author='firefly-cpp',
    url='https://github.com/firefly-cpp/PyGEtoolbox',
    license='MIT',
    classifiers=[
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development'
      ],
    include_package_data=True,
    py_modules=['PyGEtoolbox']
)
