from distutils.core import setup
from setuptools import find_packages

setup(
	name = 'piton3',
	license='LICENSE',
	packages = find_packages(), # this must be the same as the name above
	version = '0.0.2',
	author="codezed",
	author_email="zeeshanm1010@gmail.com",
	description = 'A local python package manager for python3 and pip3',
	url = 'https://github.com/piton-package-manager/piton', # use the URL to the github repo
	keywords = ['package', 'manager', 'local'], # arbitrary keywords
	classifiers = [
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.7',
	],
	entry_points = {
		'console_scripts': [
			'piton = piton.main:main'
		]
	}
)
