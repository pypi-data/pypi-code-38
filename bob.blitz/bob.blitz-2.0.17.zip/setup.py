#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['numpy', 'bob.extension']))
import numpy
from bob.extension import Extension, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

# Local include directory
import os
package_dir = os.path.dirname(os.path.realpath(__file__))
include_dir = os.path.join(package_dir, 'bob', 'blitz', 'include')

# Add numpy includes
system_include_dirs = [numpy.get_include()]

# NumPy API macros necessary?
define_macros=[
    ("PY_ARRAY_UNIQUE_SYMBOL", "BOB_BLITZ_NUMPY_C_API"),
    ("NO_IMPORT_ARRAY", "1"),
    ]
from distutils.version import LooseVersion
if LooseVersion(numpy.__version__) >= LooseVersion('1.7'):
  define_macros.append(("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"))

# Pkg-config requirements
packages = [
    'blitz >= 0.10',
    'boost', # any version will do, only need headers
    ]

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.blitz',
    version=version,
    description='Bindings for Blitz++ (a C++ array template library)',
    url='http://gitlab.idiap.ch/bob/bob.blitz',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    setup_requires = build_requires,
    install_requires = build_requires,

    ext_modules = [
      Extension("bob.blitz.version",
        [
          "bob/blitz/version.cpp",
        ],
        packages=packages,
        version=version,
        define_macros=define_macros,
        include_dirs=[include_dir],
        system_include_dirs=system_include_dirs,
      ),

      Extension("bob.blitz._library",
        [
          "bob/blitz/api.cpp",
          "bob/blitz/array.cpp",
          "bob/blitz/main.cpp",
        ],
        packages=packages,
        version=version,
        define_macros=define_macros,
        include_dirs=[include_dir],
        system_include_dirs=system_include_dirs,
      ),
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],

  )
