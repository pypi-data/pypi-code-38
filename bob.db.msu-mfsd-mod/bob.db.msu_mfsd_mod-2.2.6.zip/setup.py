#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Sushil Bhattacharjee <sushil.bhattacharjee@idiap.ch>
#Tue 10 Mar 16:07:27 CET 2015

#from setuptools import setup, find_packages
from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements
install_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='bob.db.msu_mfsd_mod',
    version=version,
    description='MSU Mobile Face Spoofing Database Access API for Bob, with modified protocol',
    url='http://gitlab.idiap.ch/bob/bob.db.msu_mfsd_mod',
    license='BSD',
    author='Ivana Chingovska, Sushil Bhattacharjee',
    author_email='ivana.chingovska@idiap.ch, sushil.bhattacharjee@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires = install_requires,
#    install_requires=[
#      'setuptools',
#      'six',
#      'bob.db.base',
#      'antispoofing.utils',
#    ],

    entry_points={

      # declare the database to bob
      'bob.db': [
        'msu_mfsd_mod = bob.db.msu_mfsd_mod.driver:Interface',
      ],


#      'console_scripts': [
#        'testme.py = bob.db.msu_mfsd_mod.testme:main',
#      ],
    },

    classifiers = [
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
