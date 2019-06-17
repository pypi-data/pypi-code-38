"""Setuptools for perfect-pypi.
	Empty example PYPI package by leecampbellc85
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import sys


here = path.abspath(path.dirname(__file__))



# Get the long description from the README file
with open("docs/readme.rst", "r") as fh:
    README = fh.read()

## Version of the current package
from perfectpypi.version import __version__

sys.stdout.write("perfect-pypi: " + __version__ + '\n')


# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(name='perfect-pypi',
	scripts=[
        'pfpy',
        'pfpy.completion.sh',
        'pfpy.bat',
    ],
	python_requires='>=2.6, <3',
    version=__version__,
	description='perfect-pypi - Empty example PYPI package by leecampbellc85',
	long_description=README,
	long_description_content_type="text/markdown",
	url='https://github.com/leecampbellc85/perfect-pypi',
	author='leecampbellc85',
	author_email='lee.campbell.c85@hotmail.com',
	keywords='python leecampbellc85hu',
	classifiers=[  # Optional
		# How mature is this project? Common values are
		#   3 - Alpha
		#   4 - Beta
		#   5 - Production/Stable
		'Development Status :: 3 - Alpha',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux',
		# Indicate who your project is intended for
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',

		# Pick your license as you wish
		'License :: OSI Approved :: MIT License',

		# Specify the Python versions you support here. In particular, ensure
		# that you indicate whether you support Python 2, Python 3 or both.
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7'
	],
	  packages=[
			'perfectpypi',
			'perfectpypi.core'
			],
		install_requires=[
			'docopt'
		],
	  license='MIT',
	  zip_safe=True)