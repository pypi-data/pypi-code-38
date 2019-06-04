# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sqlite3
from sys import version as python_version
from bottle import route, view
from bottle import __version__ as bottle_version

from _sadm import log
from _sadm.web import tpl

@route('/about')
@view('about.html')
@tpl.data('about')
def about():
	log.debug("about")
	return {
		'pythonVersion': python_version,
		'bottleVersion': bottle_version,
		'sqliteVersion': "%s (lib %s)" % (sqlite3.version, sqlite3.sqlite_version),
	}
