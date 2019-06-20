#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

setup_packages = ['bob.extension', 'bob.blitz']
bob_packages = []

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires = setup_packages + bob_packages))

# import the Extension class and the build_ext function from bob.blitz
from bob.blitz.extension import Extension, build_ext

# load the requirements.txt for additional requirements
from bob.extension.utils import load_requirements
requirements = setup_packages + bob_packages + load_requirements()

version = open("version.txt").read().rstrip()

setup(

    name='bob.ip.qualitymeasure',
    version=version,
    description='Image-quality feature-extractors for PAD applications',
    url='http://gitlab.idiap.ch/bob/bob.ip.qualitymeasure',
    license='GPLv3',
    author='Sushil Bhattacharjee',
    author_email='sushil.bhattacharjee@idiap.ch',
    maintainer="David Geissbuhler",
    maintainer_email="david.geissbuhler@idiap.ch",
    keywords='bob, image-quality, face',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,

    install_requires = requirements,

    # We are defining two extensions here. Each of them will be compiled
    # independently into a separate .so file.
    ext_modules = [

      # The first extension defines the version of this package and all C++-dependencies.
      Extension("bob.ip.qualitymeasure.version",
        # list of files compiled into this extension
        [
          "bob/ip/qualitymeasure/version.cpp",
        ],
        # additional parameters, see Extension documentation
        version = version,
        bob_packages = bob_packages,
      ),

      # The second extension contains the actual C++ code and the Python bindings
      Extension("bob.ip.qualitymeasure._library",
        # list of files compiled into this extension
        [
          # the pure C++ code
          "bob/ip/qualitymeasure/tan_specular_highlights.cpp",
          # the Python bindings
          "bob/ip/qualitymeasure/main.cpp",
        ],
        # additional parameters, see Extension documentation
        version = version,
        bob_packages = bob_packages,
      ),
    ],

    # Important! We need to tell setuptools that we want the extension to be
    # compiled with our build_ext function!
    cmdclass = {
      'build_ext': build_ext,
    },

    entry_points={
      # scripts should be declared using this entry:
      'console_scripts': [
        'compute_qualityfeatures.py = bob.ip.qualitymeasure.script.compute_qualitymeasures:main',
        'remove_highlights.py = bob.ip.qualitymeasure.script.remove_highlights:main',
      ],
    },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
