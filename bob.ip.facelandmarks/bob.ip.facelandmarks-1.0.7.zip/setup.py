#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 16 Feb 2016 15:26:26 CET

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
requirements = load_requirements()

version = open("version.txt").read().rstrip()

setup(

    name='bob.ip.facelandmarks',
    version=version,
    description='Bob wrapper for Menpo\'s face keypoint detector',
    url='http://gitlab.idiap.ch/bob/bob.ip.facelandmarks',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    keywords='bob, keypoint detection, face',
    maintainer="Sushil Bhattacharjee",
    maintainer_email="sbhatta@idiap.ch",
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,

    install_requires = requirements,

    entry_points={
      # scripts should be declared using this entry:
      'console_scripts': [
        'detect_landmarks.py = bob.ip.facelandmarks.script.detect_landmarks:main',
      ],
    },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
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
