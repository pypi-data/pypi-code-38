#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Sex 10 Ago 2012 14:22:33 CEST

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
install_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.db.replaymobile',
    version=version,
    description='Replay-Mobile Database Access API for Bob',
    url='https://gitlab.idiap.ch/bob/bob.db.replaymobile',
    license='BSD',
    author='Artur Costa-Pazo, Andre Anjos, Ivana Chingovska, Sushil Bhattacharjee',
    author_email='andre.anjos@idiap.ch, ivana.chingovska@idiap.ch, sushil.bhattacharjee@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,

    namespace_packages=[
      'bob',
      'bob.db',
    ],

    entry_points={
      # bob database declaration
      'bob.db': [
        'replaymobile = bob.db.replaymobile.driver:Interface',
      ],
    },

    classifiers=[
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
    ],
)
