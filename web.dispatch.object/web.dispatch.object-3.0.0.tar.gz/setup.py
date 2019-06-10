#!/usr/bin/env python3

from setuptools import setup
from sys import argv, version_info as python_version
from pathlib import Path


if python_version < (3, 6):
	raise SystemExit("Python 3.3 or later is required.")

here = Path(__file__).resolve().parent
version = description = url = author = None  # Populated by the next line.
exec((here / "web" / "dispatch" / "object" / "release.py").read_text('utf-8'))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-isort',  # import ordering
	]


setup(
	name = "web.dispatch.object",
	version = version,
	
	description = description,
	long_description = (here / 'README.rst').read_text('utf-8'),
	url = url,
	download_url = 'https://pypi.org/project/web.dispatch.object/releases',
	
	author = author.name,
	author_email = author.email,
	
	license = 'MIT',
	keywords = [
			'marrow',
			'dispatch',
			'web.dispatch',
			'object dispatch',
			'endpoint discovery',
			'WebCore'
		],
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Environment :: Console",
			"Environment :: Web Environment",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: 3.7",
			"Programming Language :: Python :: 3.8",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	
	project_urls = {
			"Repository": "https://github.com/marrow/web.dispatch.object/",
			"Documentation": "https://github.com/marrow/web.dispatch.object/#readme",
			"Issue Tracker": "https://github.com/marrow/web.dispatch.object/issues",
			"Funding": "https://www.patreon.com/GothAlice",
		},
	
	packages = ('web.dispatch.object', ),
	include_package_data = True,
	package_data = {'': ['README.rst', 'LICENSE.txt']},
	zip_safe = False,
	
	python_requires = '~=3.6',
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(argv) else [],
	
	install_requires = [
			'web.dispatch~=3.0.1',  # Core dispatch helpers.
		],
	
	extras_require = dict(
			development = tests_require + ['pre-commit'],  # Development-time dependencies.
		),
	
	tests_require = tests_require,
	
	# Plugin Registration
	
	entry_points = {
			'web.dispatch': [
					'object = web.dispatch.object:ObjectDispatch',
				],
		},
)
