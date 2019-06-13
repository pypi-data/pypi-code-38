#!/usr/bin/env python3
# encoding: utf-8

import re
import setuptools

with open('aioec/__init__.py') as f:
	version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open('README.rst') as f:
	readme = f.read()

setuptools.setup(
	name='aioec',
	author='Benjamin Mintz',
	author_email='bmintz@protonmail.com',
	url='https://github.com/EmoteCollector/aioec',
	version=version,
	license='MIT',
	packages=['aioec'],
	install_requires=['aiohttp>=3.3.0,<3.6.0'],
	description='async client library for the Emote Collector API',
	long_description=readme,
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Developers',
		'Topic :: Internet',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Operating System :: OS Independent',
		'License :: OSI Approved :: MIT License',
	],
)
