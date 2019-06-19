#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 30 Jan 08:45:49 2014 CET

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz']))
from bob.blitz.extension import Extension, build_ext

import os
package_dir = os.path.dirname(os.path.realpath(__file__))
include_dir = os.path.join(package_dir, 'bob', 'ip', 'draw', 'include')

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost']

setup(

    name='bob.ip.draw',
    version=version,
    description='Line and Box drawing utilities of Bob',
    url='http://gitlab.idiap.ch/bob/bob.ip.draw',
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
      Extension("bob.ip.draw.version",
        [
          "bob/ip/draw/version.cpp",
        ],
        version = version,
        packages = packages,
        include_dirs = [include_dir]
      ),
      Extension("bob.ip.draw._library",
        [
          "bob/ip/draw/point.cpp",
          "bob/ip/draw/try_point.cpp",
          "bob/ip/draw/line.cpp",
          "bob/ip/draw/cross.cpp",
          "bob/ip/draw/box.cpp",
          "bob/ip/draw/main.cpp",
        ],
        packages = packages,
        version = version,
        include_dirs = [include_dir]
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
