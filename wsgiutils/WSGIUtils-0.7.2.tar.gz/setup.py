#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.join(os.getcwd(),'lib'))

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

import wsgiutils

try:
	os.remove ('MANIFEST')
except:
	pass

with open(os.path.join(os.getcwd(), 'README.txt'), 'r') as _readme:
	long_description = _readme.read()

setup(name="WSGIUtils",
	version= wsgiutils.__version__,
	description="WSGI Utils are a collection of useful libraries for use in a WSGI environnment.",
	long_description=long_description,
	author="Colin Stewart",
	author_email="colin@owlfish.com",
	license="BSD-3-Clause",
	url="https://www.owlfish.com/software/wsgiutils/index.html",
	project_urls={
		"Source Code": "https://github.com/davidfraser/WSGIUtils/",
		"Documentation": "https://www.owlfish.com/software/wsgiutils/documentation/index.html",
	},
	packages=[
		'wsgiutils',
	],
	package_dir = {'': 'lib'},
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Internet :: WWW/HTTP :: WSGI',
	],
)
