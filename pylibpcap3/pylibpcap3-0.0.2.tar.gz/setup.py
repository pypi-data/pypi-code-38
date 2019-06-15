from setuptools import setup, find_packages

setup(
	# Application name:
	name="pylibpcap3",

	# Version number (initial):
	version="0.0.2",

	# Application author details:
	author="Tamas Jos",
	author_email="info@skelsec.com",

	# Packages
	packages=find_packages(),

	# Include additional files into the package
	include_package_data=True,


	# Details
	url="https://github.com/skelsec/pylibpcap3",

	zip_safe = True,
	#
	# license="LICENSE.txt",
	description="ctypes libPCAP bindings for python3",

	# long_description=open("README.txt").read(),
	python_requires='>=3.7',
	
	classifiers=(
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	),
)
