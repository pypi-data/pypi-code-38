#! /usr/bin/env python
# coding=utf-8

import os
import sys

from setuptools import setup
from setuptools.extension import Extension

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Version

with open(os.path.join('koho', '_version.py')) as f:
    exec(f.read())
VERSION = __version__

# C++ implementation with Cython bindings

if '--use-cython' in sys.argv:
    sys.argv.remove('--use-cython')
    from Cython.Build import cythonize
    cython_extensions = cythonize([
        Extension(name='koho.sklearn._decision_tree_cpp',
                  sources=['koho/sklearn/_decision_tree_cpp.pyx',
                           'koho/cpp/random_number_generator.cpp',
                           'koho/cpp/decision_tree.cpp'],
                  extra_compile_args=['-std=c++17'],
                  language='c++')])
else:
    cython_extensions = [
        Extension(name='koho.sklearn._decision_tree_cpp',
                  sources=['koho/sklearn/_decision_tree_cpp.cpp',
                           'koho/cpp/random_number_generator.cpp',
                           'koho/cpp/decision_tree.cpp'],
                  extra_compile_args=['-std=c++17'],
                  language='c++')]

setup(name='koho',
      version=VERSION,
      description='Decision Forest C++ library with a scikit-learn compatible Python interface',
      license='New BSD License',
      packages=['koho','koho.sklearn'],
      author='AI Werkstatt(TM) www.aiwerkstatt.com',
      author_email='drh@aiwerkstatt.com',
      maintainer='AI Werkstatt(TM) www.aiwerkstatt.com',
      maintainer_email='drh@aiwerkstatt.com',
      url='https://koho.readthedocs.io/en/latest/',
      download_url='https://github.com/aiwerkstatt/koho',
      long_description=read("README.rst"),
      zip_safe=False,  # the package can run out of an .egg file
      ext_modules = cython_extensions,
      package_data={'': ['*.pyx', '*.cpp', 'cpp/random_number_generator.h', 'cpp/decision_tree.h', 'cpp/utilities.h']},
      install_requires=['numpy', 'scipy', 'scikit-learn'],
      extras_require={
          'tests': ['pytest', 'pytest-cov'],
          'docs': ['sphinx', 'sphinx-gallery', 'sphinx_rtd_theme', 'matplotlib']},
      classifiers=[
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'License :: OSI Approved :: BSD License',
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Cython',
          'Programming Language :: C',
          'Programming Language :: C++',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix']
      )
