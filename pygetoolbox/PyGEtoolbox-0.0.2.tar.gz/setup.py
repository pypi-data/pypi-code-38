# -*- coding: utf-8 -*-

from setuptools import setup
import os
import sys

with open('README.md') as f:
    readme = f.read()

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('PyGEtoolbox/')

setup(
    name='PyGEtoolbox',
    version='0.0.2',
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
    install_requires=[
          'pandas',
	  'urllib2'
      ],
    packages = ['PyGEtoolbox'],
    package_data={'': extra_files}
    
)
