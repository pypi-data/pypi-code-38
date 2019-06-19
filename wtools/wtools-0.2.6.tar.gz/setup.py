#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import sys
from setuptools import setup
import wtools


url = "https://bitbucket.org/Moo7/wtools"
here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here,'README.md')) as f:
	long_description = f.read()


setup(
	name = "wtools",
	version = wtools.version,
	author = "Michel Mooij",
	author_email = "michel.mooij7@gmail.com",
	maintainer = "Michel Mooij",
	maintainer_email = "michel.mooij7@gmail.com",
	url = url,
	download_url = "%s/downloads/wtools-%s.tar.gz" % (url, wtools.version),
	description = "WAF build tools",
	long_description = long_description,
	packages = ["wtools"],
	install_requires = ["distro"],
	license = 'MIT',
	keywords = ["waf", "c", "c++", "eclipse", "make", ".rpm", ".deb", ".ipk", "ipkg"],
	platforms = 'any',
	entry_points = {
		'console_scripts': [
			['wbox = wtools.box:main'],
			['waf-get = wtools.waf:main']
		],
	},
	classifiers = [
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: Microsoft :: Windows :: Windows 10",
		"Operating System :: Microsoft :: Windows :: Windows 7",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: C",
		"Programming Language :: C++",
		"Programming Language :: Python :: 3.5",
		"Topic :: Software Development :: Build Tools",
		"Topic :: Software Development :: Embedded Systems",
		"Topic :: Utilities",
	],
)

