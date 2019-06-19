#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

bob_packages = ['bob.core', 'bob.io.base', 'bob.math', 'bob.learn.activation']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension','bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, Library, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost']
boost_modules = ['system']

setup(

    name='bob.learn.mlp',
    version=version,
    description='Multi-layer Perceptron and Trainers for Bob',
    url='http://gitlab.idiap.ch/bob/bob.learn.mlp',
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
      Extension("bob.learn.mlp.version",
        [
          "bob/learn/mlp/version.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Library("bob.learn.mlp.bob_learn_mlp",
        [
          "bob/learn/mlp/cxx/roll.cpp",
          "bob/learn/mlp/cxx/machine.cpp",
          "bob/learn/mlp/cxx/cross_entropy.cpp",
          "bob/learn/mlp/cxx/square_error.cpp",
          "bob/learn/mlp/cxx/shuffler.cpp",
          "bob/learn/mlp/cxx/trainer.cpp",
          "bob/learn/mlp/cxx/backprop.cpp",
          "bob/learn/mlp/cxx/rprop.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Extension("bob.learn.mlp._library",
        [
          "bob/learn/mlp/roll.cpp",
          "bob/learn/mlp/rprop.cpp",
          "bob/learn/mlp/backprop.cpp",
          "bob/learn/mlp/trainer.cpp",
          "bob/learn/mlp/shuffler.cpp",
          "bob/learn/mlp/cost.cpp",
          "bob/learn/mlp/machine.cpp",
          "bob/learn/mlp/main.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
      ),
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    entry_points={
      'console_scripts': [
      ],
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
