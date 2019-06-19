#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

bob_packages = ['bob.core', 'bob.io.base']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, Library, build_ext
from bob.extension import pkgconfig, find_library

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

import os
package_dir = os.path.dirname(os.path.realpath(__file__))
target_dir = os.path.join(package_dir, 'bob', 'io', 'audio')

packages = [
  'boost',
  'sox',
  ]

setup(

    name='bob.io.audio',
    version=version,
    description='Audio I/O support for Bob',
    url='http://gitlab.idiap.ch/bob/bob.io.audio',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires = build_requires,

    ext_modules = [
      Extension("bob.io.audio.version",
        [
          "bob/io/audio/version.cpp",
        ],
        packages = packages,
        boost_modules = ['system'],
        bob_packages = bob_packages,
        version = version,
      ),

      Extension("bob.io.audio._library",
        [
          "bob/io/audio/cpp/utils.cpp",
          "bob/io/audio/cpp/reader.cpp",
          "bob/io/audio/cpp/writer.cpp",
          "bob/io/audio/bobskin.cpp",
          "bob/io/audio/reader.cpp",
          "bob/io/audio/writer.cpp",
          "bob/io/audio/file.cpp",
          "bob/io/audio/main.cpp",
        ],
        packages = packages,
        boost_modules = ['system'],
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
