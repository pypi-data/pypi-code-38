#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 30 Jan 08:45:49 2014 CET

bob_packages = ['bob.core']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, Library, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

setup(

    name='bob.sp',
    version=version,
    description="Core signal processing utilities for Bob",
    url='http://gitlab.idiap.ch/bob/bob.sp',
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
      Extension("bob.sp.version",
        [
          "bob/sp/version.cpp",
        ],
        version = version,
        bob_packages = bob_packages,
      ),

      Library('bob.sp.bob_sp',
        [
          "bob/sp/cpp/DCT1DNaive.cpp",
          "bob/sp/cpp/DCT2D.cpp",
          "bob/sp/cpp/DCT2DNaive.cpp",
          "bob/sp/cpp/FFT1D.cpp",
          "bob/sp/cpp/FFT2DNaive.cpp",
          "bob/sp/cpp/DCT1D.cpp",
          "bob/sp/cpp/FFT1DNaive.cpp",
          "bob/sp/cpp/FFT2D.cpp",
          "bob/sp/cpp/fftpack.c"
        ],
        version = version,
        bob_packages = bob_packages,
      ),

      Extension("bob.sp._library",
        [
          "bob/sp/quantization.cpp",
          "bob/sp/extrapolate.cpp",
          "bob/sp/fft1d.cpp",
          "bob/sp/fft2d.cpp",
          "bob/sp/ifft1d.cpp",
          "bob/sp/ifft2d.cpp",
          "bob/sp/fft.cpp",
          "bob/sp/dct1d.cpp",
          "bob/sp/dct2d.cpp",
          "bob/sp/idct1d.cpp",
          "bob/sp/idct2d.cpp",
          "bob/sp/dct.cpp",
          "bob/sp/main.cpp",
        ],
        version = version,
        bob_packages = bob_packages,
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
