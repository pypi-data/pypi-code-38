# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import unlink, path
from sqlite3 import Connection, Row

from _sadm import log
from _sadm.web import syslog

_dbfile = './tdata/tmp/web/syslog.db'
syslog._dbfile = _dbfile

def _cleanup():
	if path.isfile(_dbfile):
		unlink(_dbfile)
	assert not path.isfile(_dbfile), 'could not cleanup'

def _dbInit():
	assert syslog._dbfile == _dbfile, 'not using testing db file'
	assert not path.isfile(_dbfile), 'dbfile already exists!'
	return syslog._dbInit()

_cleanup()

def test_dbInit():
	db = _dbInit()
	assert isinstance(db, Connection), 'wrong instance'
	assert db.row_factory == Row, 'wrong db row_factory'
	db.close()
	assert path.isfile(_dbfile), 'db not created'
	_cleanup()

def test_initClose():
	assert isinstance(syslog._logger, syslog._webLogger), \
		'wrong instance'
	assert syslog._logger.db is None, \
		'_logger.db should be None'
	assert isinstance(log._logger, log._dummyLogger), \
		'main logger wrong instance'
	assert log._logger._child is None, \
		'main logger._child should be None'
	syslog.init()
	assert isinstance(syslog._logger.db, Connection), \
		'wrong db instance'
	assert isinstance(log._logger, log._dummyLogger), \
		'main logger wrong instance'
	assert isinstance(log._logger._child, syslog._webLogger), \
		'wrong instance'
	syslog.close()
	assert isinstance(log._logger._child, log._dummyLogger), \
		'wrong instance'
	_cleanup()

def test_initError():
	assert not path.isfile(_dbfile), 'db exists'
	syslog._dbfile = '/i/hope/this/is/invalid/enough/syslog.db'
	syslog.init()
	syslog._dbfile = _dbfile
	assert not path.isfile(_dbfile), 'db was created, so no error happen'

def test_logger():
	l = syslog._logger
	syslog.init()
	assert isinstance(l, syslog._webLogger), 'wrong instance'
	l.error('test.error')
	l.warn('test.warn')
	l.info('test.info')
	l.msg('test.msg')
	assert syslog._getMsgId(0) is None
	msg = syslog._getMsgId(1)
	assert msg[0] == 1
	assert msg[2] == syslog._LVLMAP['error']
	assert msg[3] == 'test.error'
	msg = syslog._getMsgId(2)
	assert msg[0] == 2
	assert msg[2] == syslog._LVLMAP['warn']
	assert msg[3] == 'test.warn'
	msg = syslog._getMsgId(3)
	assert msg[0] == 3
	assert msg[2] == syslog._LVLMAP['info']
	assert msg[3] == 'test.info'
	msg = syslog._getMsgId(4)
	assert msg[0] == 4
	assert msg[2] == syslog._LVLMAP['msg']
	assert msg[3] == 'test.msg'
	syslog.close()
	_cleanup()

def test_lastMsgs():
	l = syslog._logger
	syslog.init()
	assert isinstance(l, syslog._webLogger), 'wrong instance'
	l.error('test.error')
	l.warn('test.warn')
	l.info('test.info')
	l.msg('test.msg')
	assert syslog._getMsgId(0) is None
	msgs = syslog.last(10)
	assert isinstance(msgs, list)
	assert isinstance(msgs[0], Row)
	assert len(msgs) == 4
	idx = 0
	for m in msgs:
		idx += 1
		assert m['id'] == idx
	assert msgs[0]['msg'] == 'test.error'
	assert msgs[1]['msg'] == 'test.warn'
	assert msgs[2]['msg'] == 'test.info'
	assert msgs[3]['msg'] == 'test.msg'
	msgs = syslog.last(2)
	assert len(msgs) == 2
	assert msgs[0]['msg'] == 'test.info'
	assert msgs[1]['msg'] == 'test.msg'
