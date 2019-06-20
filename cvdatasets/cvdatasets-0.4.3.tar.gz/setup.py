#!/usr/bin/env python

import os
import pkg_resources
import sys

from setuptools import setup, find_packages

try: # for pip >= 10
	from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
	from pip.req import parse_requirements

here = os.path.abspath(os.path.dirname(__file__))
# Get __version__ variable
exec(open(os.path.join(here, 'cvdatasets', '_version.py')).read())

install_requires = [
	line.strip()
		for line in open("requirements.txt").readlines()
]

setup(
	name='cvdatasets',
	version=__version__,
	description='Wrapper (inofficial) for NA-Birds bataset (http://dl.allaboutbirds.org/nabirds)',
	author='Dimitri Korsch',
	author_email='korschdima@gmail.com',
	license='MIT License',
	packages=find_packages(),
	zip_safe=False,
	setup_requires=[],
	install_requires=install_requires,
	package_data={'': ['requirements.txt']},
	data_files=[('.',['requirements.txt'])],
	include_package_data=True,
)
