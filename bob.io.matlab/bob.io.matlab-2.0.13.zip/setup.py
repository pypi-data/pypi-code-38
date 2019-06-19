#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

bob_packages = ['bob.core', 'bob.io.base']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost', 'matio >= 1.3.0']
boost_modules = ['system']

setup(

    name='bob.io.matlab',
    version=version,
    description='Handling of Matlab(R) files via bob.io.base',
    url='http://gitlab.idiap.ch/bob/bob.io.matlab',
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
      Extension("bob.io.matlab.version",
        [
          "bob/io/matlab/version.cpp",
        ],
        packages = packages,
        boost_modules = boost_modules,
        bob_packages = bob_packages,
        version = version,
      ),

      Extension("bob.io.matlab._library",
        [
          "bob/io/matlab/bobskin.cpp",
          "bob/io/matlab/utils.cpp",
          "bob/io/matlab/file.cpp",
          "bob/io/matlab/main.cpp",
        ],
        packages = packages,
        boost_modules = boost_modules,
        bob_packages = bob_packages,
        version = version,
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
      'Environment :: Plugins',
    ],

  )
