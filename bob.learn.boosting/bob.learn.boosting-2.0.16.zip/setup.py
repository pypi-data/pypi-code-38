#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

bob_packages = ['bob.core', 'bob.io.base']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

version = open("version.txt").read().rstrip()

# Local include directory
import os
package_dir = os.path.dirname(os.path.realpath(__file__))
include_dir = os.path.join(package_dir, 'bob', 'learn', 'boosting', 'include')

packages = ['boost']
boost_modules = ['system']

setup(
    name='bob.learn.boosting',
    version=version,
    description='Boosting framework for Bob',
    url='https://gitlab.idiap.ch/bob/bob.learn.boosting',
    license='BSD',
    author='Manuel Guenther (with help of Rakesh Mehta)',
    author_email='manuel.guenther@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    setup_requires = build_requires,
    install_requires = build_requires,

    ext_modules = [
      Extension("bob.learn.boosting.version",
        [
          "bob/learn/boosting/version.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
        include_dirs=[include_dir],
      ),

      Extension(
        'bob.learn.boosting._library',
        [
          "bob/learn/boosting/main.cpp",
          "bob/learn/boosting/loss_function.cpp",
          "bob/learn/boosting/jesorsky_loss.cpp",
          "bob/learn/boosting/weak_machine.cpp",
          "bob/learn/boosting/stump_machine.cpp",
          "bob/learn/boosting/lut_machine.cpp",
          "bob/learn/boosting/boosted_machine.cpp",
          "bob/learn/boosting/lut_trainer.cpp",

          # old Library components
          "bob/learn/boosting/cpp/LossFunction.cpp",
          "bob/learn/boosting/cpp/JesorskyLoss.cpp",
          "bob/learn/boosting/cpp/StumpMachine.cpp",
          "bob/learn/boosting/cpp/LUTMachine.cpp",
          "bob/learn/boosting/cpp/BoostedMachine.cpp",
          "bob/learn/boosting/cpp/LUTTrainer.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
        include_dirs=[include_dir],
      ),
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    entry_points={
      'console_scripts': [
        'boosting_example.py = bob.learn.boosting.examples.mnist:main',
      ],
    },

    # https://pypi.org/classifiers/
    classifiers = [
      'Framework :: Bob',
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
