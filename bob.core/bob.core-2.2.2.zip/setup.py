#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz']))
from bob.blitz.extension import Extension, Library, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['blitz >= 0.10', 'boost']

setup(

    name='bob.core',
    version=version,
    description='Core utilities required on all Bob modules',
    url='http://gitlab.idiap.ch/bob/bob.core',
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
      Extension("bob.core.version",
        [
          "bob/core/version.cpp",
        ],
        version = version,
        packages = packages,
        boost_modules = ['system']
      ),

      Library("bob.core.bob_core",
        [
          "bob/core/cpp/logging.cpp",
        ],
        version = version,
        packages = packages,
        boost_modules = ['system', 'iostreams', 'filesystem'],
      ),

      Extension("bob.core._convert",
        [
          "bob/core/convert.cpp",
        ],
        version = version,
        packages = packages,
      ),

      Extension("bob.core._logging",
        [
          "bob/core/logging.cpp",
        ],
        version = version,
        packages = packages,
        boost_modules = ['system', 'iostreams', 'filesystem'],
      ),

      Extension("bob.core.random._library",
        [
          "bob/core/random/mt19937.cpp",
          "bob/core/random/uniform.cpp",
          "bob/core/random/normal.cpp",
          "bob/core/random/lognormal.cpp",
          "bob/core/random/gamma.cpp",
          "bob/core/random/binomial.cpp",
          "bob/core/random/discrete.cpp",
          "bob/core/random/main.cpp",
        ],
        version = version,
        packages = packages,
        boost_modules = ['system', 'iostreams', 'filesystem'],
      ),

      Extension("bob.core._test",        [
          "bob/core/test.cpp",
        ],
        version = version,
        packages = packages,
        boost_modules = ['system', 'iostreams', 'filesystem'],
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
