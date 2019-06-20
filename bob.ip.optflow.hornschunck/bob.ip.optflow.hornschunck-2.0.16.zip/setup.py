#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Sep 2012 14:43:19 CEST

"""Bindings for optical flow from Horn & Schunck
"""

bob_packages = ['bob.core', 'bob.sp']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

setup(

    name="bob.ip.optflow.hornschunck",
    version=version,
    description="Optical Flow framework based on Horn & Schunck",
    license="BSD",
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),
    url='https://gitlab.idiap.ch/bob/bob.ip.optflow.hornschunck',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    setup_requires = build_requires,
    install_requires = build_requires,

    ext_modules = [
      Extension("bob.ip.optflow.hornschunck.version",
        [
          "bob/ip/optflow/hornschunck/version.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
      ),

      Extension("bob.ip.optflow.hornschunck._library",
        [
          "bob/ip/optflow/hornschunck/SpatioTemporalGradient.cpp",
          "bob/ip/optflow/hornschunck/HornAndSchunckFlow.cpp",
          "bob/ip/optflow/hornschunck/forward.cpp",
          "bob/ip/optflow/hornschunck/central.cpp",
          "bob/ip/optflow/hornschunck/vanilla.cpp",
          "bob/ip/optflow/hornschunck/flow.cpp",
          "bob/ip/optflow/hornschunck/main.cpp",
        ],
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
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Scientific/Engineering :: Image Recognition',
    ],

)
