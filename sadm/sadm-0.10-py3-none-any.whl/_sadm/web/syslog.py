# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys
import sqlite3
from os import path, makedirs

from _sadm import log

# SQL stuff

_DB_CREATE = """
CREATE TABLE syslog (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	time TEXT DEFAULT CURRENT_TIMESTAMP,
	level INTEGER,
	msg TEXT
);
"""
_LVLMAP = {
	'error': 3,
	'warn': 2,
	'info': 1,
	'msg': 0,
}
_LOG_INSERT = 'INSERT INTO syslog (level, msg) VALUES (?, ?)'
_GET_MSG_ID = 'SELECT id, time, level, msg FROM syslog WHERE id = ?'
_GET_LAST = 'SELECT id, time, level, msg FROM syslog ORDER BY id DESC LIMIT ?'

# underlying logger class

class _webLogger(object):
	db = None

	def error(self, msg):
		self.db.execute(_LOG_INSERT, (_LVLMAP['error'], msg))
		self.db.commit()
		# ~ print("[syslog] E:", msg, file = sys.stderr)

	def warn(self, msg):
		self.db.execute(_LOG_INSERT, (_LVLMAP['warn'], msg))
		self.db.commit()
		# ~ print("[syslog] W:", msg, file = sys.stderr)

	def info(self, msg):
		self.db.execute(_LOG_INSERT, (_LVLMAP['info'], msg))
		self.db.commit()
		# ~ print("[syslog] I:", msg, file = sys.stdout)

	def msg(self, msg):
		self.db.execute(_LOG_INSERT, (_LVLMAP['msg'], msg))
		self.db.commit()
		# ~ print("[syslog]", msg, file = sys.stdout)

def _dbInit():
	log.debug("syslog init %s" % _dbfile)
	log.debug("sqlite version %s (lib %s)" % (sqlite3.version, sqlite3.sqlite_version))
	mkdb = not path.isfile(_dbfile)
	if mkdb:
		dbdir = path.dirname(_dbfile)
		makedirs(dbdir, mode = 0o700, exist_ok = True)
	db = sqlite3.connect(_dbfile)
	db.row_factory = sqlite3.Row
	return _dbCheck(db, mkdb)

def _dbCheck(db, create):
	if create:
		log.debug('create syslog db')
		db.executescript(_DB_CREATE)
		db.commit()
	return db

# default logger

_logger = _webLogger()
_dbfile = path.expanduser('~/.local/sadm/syslog.db')

def _getMsgId(msgid):
	return _logger.db.execute(_GET_MSG_ID, [str(msgid)]).fetchone()

# public methods

def init():
	log.debug('init web syslog')
	try:
		_logger.db = _dbInit()
	except Exception as err:
		log.debug("exception: %s" % type(err))
		log.error("could not init web syslog: %s" % err)
	else:
		log.debug('attach child logger')
		log._logger._child = _logger
		log.info('syslog start')

def close():
	if _logger.db is not None:
		log.info('syslog end')
		_logger.db.close()
		log._logger._child = log._dummyLogger()

def last(limit):
	msgs = _logger.db.execute(_GET_LAST, [str(limit)]).fetchall()
	msgs.reverse()
	return msgs
