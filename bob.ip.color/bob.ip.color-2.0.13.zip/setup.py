#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 30 Jan 08:45:49 2014 CET

bob_packages = ['bob.core', 'bob.io.base']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, Library, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost']
boost_modules = ['system']

setup(

    name='bob.ip.color',
    version=version,
    description='Color Conversion Utilities of Bob',
    url='http://gitlab.idiap.ch/bob/bob.ip.color',
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
      Extension("bob.ip.color.version",
        [
          "bob/ip/color/version.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Library("bob.ip.color.bob_ip_color",
        [
          "bob/ip/color/cpp/color.cpp",
        ],
        version = version,
        bob_packages = bob_packages,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Extension("bob.ip.color._library",
        [
          "bob/ip/color/utils.cpp",
          "bob/ip/color/rgb_to_gray.cpp",
          "bob/ip/color/rgb_to_yuv.cpp",
          "bob/ip/color/rgb_to_hsv.cpp",
          "bob/ip/color/rgb_to_hsl.cpp",
          "bob/ip/color/main.cpp",
        ],
        version = version,
        bob_packages = bob_packages,
        packages = packages,
        boost_modules = boost_modules,
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
