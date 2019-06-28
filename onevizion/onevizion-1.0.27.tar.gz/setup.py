#!/usr/bin/env python

import os
from setuptools import setup, find_packages
#from onevizion import __version__
__version__ = '1.0.27'

#following PyPI guide: https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/

def read(*paths):
	"""Build a file path from *paths* and return the contents."""
	from io import open
	with open(os.path.join(*paths), 'rb') as f:
		return bytes(f.read())

ReadMeFileText = read('README.md')

setup(name='onevizion',
	version = __version__,
	author="OneVizion",
	author_email="development@onevizion.com",
	url="https://github.com/Onevizion/API-v3",
	classifiers=[
	"Development Status :: 4 - Beta",
	"Environment :: Console",
	"Intended Audience :: System Administrators",
	"License :: OSI Approved :: MIT License",
	"Operating System :: Unix",
	"Programming Language :: Python",
	],
	py_modules = ['onevizion'],

	platforms=["Unix"],
	license="MIT",
	description="onevizion wraps the version 3 API for a OneVizion system, and provides a few optional other utilities."
)
