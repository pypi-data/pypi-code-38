#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

# https://packaging.python.org/guides/distributing-packages-using-setuptools/

from sys import argv
from os import makedirs, path, unlink
from setuptools import setup, find_packages

def main():

	try:
		cmd = argv[1]
	except IndexError:
		cmd = 'none'

	if cmd in ['build', 'dist']:
		_build()
	elif cmd == 'clean':
		_clean()

	with open('requirements.txt', 'r') as fh:
		deps = fh.read().splitlines()

	setup(
		author = 'Jeremías Casteglione',
		author_email = 'jrmsdev@gmail.com',
		python_requires = '~=3.4',
		setup_requires = ['setuptools_scm>=3.3'],
		install_requires = deps,
		use_scm_version = {'write_to': '_sadm/_version.py'},
		py_modules = ['sadm'],
		packages = find_packages(),
		include_package_data = True,
	)

def _build():
	if not path.isfile('./build/.gitignore'):
		makedirs('./build', exist_ok = True)
		with open('./build/.gitignore', 'w') as fh:
			fh.write('*\n')

def _clean():
	if path.isfile('./build/.gitignore'):
		unlink('./build/.gitignore')

if __name__ == '__main__':
	main()
