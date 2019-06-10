#!/usr/bin/env python3

from setuptools import setup
from sys import argv, version_info as python_version
from pathlib import Path

if python_version < (3, 6):
	raise SystemExit("Python 3.6 or later is required.")

here = Path(__file__).resolve().parent
version = description = url = author = author_email = ""  # Populated by the next line.
exec((here / "web" / "db" / "release.py").read_text('utf-8'))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pymongo',  # database connector
		'mongoengine',  # database connector
		'sqlalchemy',  # database connector
	]


setup(
	name = "web.db",
	version = version,
	
	description = description,
	long_description = (here / 'README.rst').read_text('utf-8'),
	url = url,
	download_url = 'https://github.com/marrow/web.db/releases',
	
	author = author.name,
	author_email = author.email,
	license = 'MIT',
	keywords = [
			'marrow',
			'web.ext',
			'web.db',
			'WebCore',
			'database connector',
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
			"Topic :: Software Development :: Libraries",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	
	project_urls = {
			"Repository": "https://github.com/marrow/web.db/",
			"Documentation": "https://github.com/marrow/web.db/#readme",
			"Issue Tracker": "https://github.com/marrow/web.db/issues",
			"Funding": "https://www.patreon.com/GothAlice",
		},
	
	packages = ('web.db', 'web.ext'),
	include_package_data = True,
	package_data = {'': ['README.rst', 'LICENSE.txt']},
	zip_safe = False,
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(argv) else [],
	
	install_requires = [
			'marrow.package~=2.0.0',  # dynamic execution and plugin management
			'WebCore~=3.0.0',  # web framework dependency
		],
	
	extras_require = dict(
			development = tests_require + ['pre-commit'],  # Development-time dependencies.
		),
	
	tests_require = tests_require,
	
	entry_points = {
		'web.extension': [  # WebCore Framework Extensions
				'db = web.ext.db:DatabaseExtension',
			],
		
		'web.db': [  # Database Connectors
				'sqlalchemy = web.db.sa:SQLAlchemyDBConnection',
				'pymongo = web.db.mongo:MongoDBConnection',
				'mongoengine = web.db.me:MongoEngineDBConnection',
				'dbapi = web.db.dbapi:DBAPIConnection',
				'sqlite3 = web.db.dbapi:SQLite3Connection',
			],
		},
)
