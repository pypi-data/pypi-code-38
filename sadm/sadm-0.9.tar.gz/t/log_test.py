# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

# https://docs.pytest.org/en/latest/assert.html

import io
from pytest import raises
from _sadm import log

def test_getCaller():
	assert log._getCaller(1).startswith('t/log_test.py:')

def test_levels():
	assert sorted(log.levels()) == ['debug', 'error', 'info', 'msg', 'quiet', 'warn']
	assert log.defaultLevel() == 'warn'

def test_dummyLogger():
	log._logger = log._dummyLogger()
	log.debug('')
	log.error('')
	log.warn('')
	log.info('')
	log.msg('')

def _sysLogger(level):
	s = io.StringIO()
	return log._sysLogger(level, outs = s), s

def test_lvlDebug():
	l, s = _sysLogger('debug')
	assert l is not None
	assert s is not None
	l.debug('test')
	assert s.getvalue().startswith('D: ')
	assert s.getvalue().endswith(': test\n')
	l.error('test')
	assert s.getvalue().endswith('\nE: test\n')
	l.warn('test')
	assert s.getvalue().endswith('\nW: test\n')
	l.info('test')
	assert s.getvalue().endswith('\nI: test\n')
	l.msg('test')
	assert s.getvalue().endswith('\ntest\n')

def test_lvlInfo():
	l, s = _sysLogger('info')
	l.debug('test')
	assert '' == s.getvalue()
	l.error('test')
	assert 'E: test\n' == s.getvalue()
	l.info('test')
	assert s.getvalue().endswith('\nI: test\n')
	l.msg('test')
	assert s.getvalue().endswith('\ntest\n')
	l.warn('test')
	assert s.getvalue().endswith('\nW: test\n')

def test_lvlWarn():
	l, s = _sysLogger('warn')
	l.debug('test')
	assert '' == s.getvalue()
	l.info('test')
	assert '' == s.getvalue()
	l.warn('test')
	assert 'W: test\n' == s.getvalue()
	l.error('test')
	assert s.getvalue().endswith('\nE: test\n')
	l.msg('test')
	assert s.getvalue().endswith('\ntest\n')

def test_lvlMsg():
	l, s = _sysLogger('msg')
	l.debug('test')
	assert '' == s.getvalue()
	l.info('test')
	assert '' == s.getvalue()
	l.warn('test')
	assert '' == s.getvalue()
	l.error('test')
	assert 'E: test\n' == s.getvalue()
	l.msg('test')
	assert s.getvalue().endswith('\ntest\n')

def test_lvlError():
	l, s = _sysLogger('error')
	l.debug('test')
	assert '' == s.getvalue()
	l.warn('test')
	assert '' == s.getvalue()
	l.info('test')
	assert '' == s.getvalue()
	l.msg('test')
	assert '' == s.getvalue()
	l.error('test')
	assert 'E: test\n' == s.getvalue()

def test_lvlQuiet():
	l, s = _sysLogger('quiet')
	l.debug('test')
	assert '' == s.getvalue()
	l.warn('test')
	assert '' == s.getvalue()
	l.info('test')
	assert '' == s.getvalue()
	l.msg('test')
	assert '' == s.getvalue()
	l.error('test')
	assert '' == s.getvalue()

def test_lvlInvalid():
	with raises(RuntimeError, match = 'invalid log level: invalid'):
		log._sysLogger('invalid')

def test_debugDepth():
	l, s = _sysLogger('debug')
	l.debug('test', depth = 2)
	assert s.getvalue().startswith('D: t/log_test.py:')

def test_debugTag():
	l, s = _sysLogger('debug')
	l.debug('test', tag = 'tag')
	assert s.getvalue().startswith('D: tag ')
