# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys

# colors

_colored = sys.stdout.isatty() and sys.stderr.isatty()

_colDebug = lambda msg: 'D: ' + msg
_colWarn = lambda msg: 'W: ' + msg
_colError = lambda msg: 'E: ' + msg
_colInfo = lambda msg: 'I: ' + msg
_colMsg = lambda msg: msg

_cyan = '\033[0;36m'
_red = '\033[0;31m'
_yellow = '\033[0;33m'
_blue = '\033[0;34m'
_green = '\033[0;32m'
_grey = '\033[1;30m'
_reset = '\033[0m'

# ~ _colored = False
def _setColored():
	global _colDebug
	global _colWarn
	global _colError
	global _colInfo
	global _colMsg
	if _colored: # pragma: no cover
		_colDebug = lambda msg: _grey + msg + _reset
		_colError = lambda msg: _red + msg + _reset
		_colWarn = lambda msg: _yellow + msg + _reset
		_colInfo = lambda msg: _blue + msg + _reset
		_colMsg = lambda msg: _green + msg + _reset

# debug file info

_idx = __file__.find('_sadm')

def _getCaller(depth):
	inf = sys._getframe(depth)
	return "%s:%d" % (inf.f_code.co_filename[_idx:], inf.f_lineno)

# setup logger

class _sysLogger(object):

	def __init__(self, level, outs = None):
		self._depth = 3
		self._child = _dummyLogger()
		self._outs = sys.stdout
		self._errs = sys.stderr
		if outs is not None:
			self._outs = outs
			self._errs = outs
		self.debug = self._off
		self.warn = self._off
		self.error = self._off
		self.info = self._off
		self.msg = self._off
		self._initLevel(level)

	def _initLevel(self, level):
		# debug: all messages
		if level == 'debug':
			self.debug = self._debug
			self.warn = self._warn
			self.info = self._info
			self.msg = self._msg
			self.error = self._error
		# info: info + warn + msg + error
		elif level == 'info':
			self.debug = self._off
			self.warn = self._warn
			self.info = self._info
			self.msg = self._msg
			self.error = self._error
		# warn: warn + msg + error
		elif level == 'warn':
			self.debug = self._off
			self.info = self._off
			self.warn = self._warn
			self.msg = self._msg
			self.error = self._error
		# msg: msg + error
		elif level == 'msg':
			self.debug = self._off
			self.info = self._off
			self.warn = self._off
			self.msg = self._msg
			self.error = self._error
		# error: only errors
		elif level == 'error':
			self.debug = self._off
			self.warn = self._off
			self.info = self._off
			self.msg = self._off
			self.error = self._error
		# quiet: no messages
		elif level == 'quiet':
			self.debug = self._off
			self.warn = self._off
			self.info = self._off
			self.msg = self._off
			self.error = self._off
		else:
			raise RuntimeError("invalid log level: %s" % level)

	def _off(self, msg, depth = None, tag = None):
		pass

	def _debug(self, msg, depth = None, tag = None):
		if tag is None:
			tag = ''
		else:
			tag = tag.strip()
			tag += ' '
		if depth is None:
			depth = self._depth
		caller = _getCaller(depth)
		print(_colDebug("%s%s: %s" % (tag, caller, msg)), file = self._errs)
		# no debug info for child logger

	def _error(self, msg):
		print(_colError(msg), file = self._errs)
		self._child.error(msg)

	def _warn(self, msg):
		print(_colWarn(msg), file = self._errs)
		self._child.warn(msg)

	def _info(self, msg):
		print(_colInfo(msg), file = self._outs)
		self._child.info(msg)

	def _msg(self, msg):
		print(_colMsg(msg), file = self._outs)
		self._child.msg(msg)

class _dummyLogger(object):

	def __init__(self):
		self._child = None

	def debug(self, msg, depth = None, tag = None):
		pass

	def error(self, msg):
		pass

	def warn(self, msg):
		pass

	def info(self, msg):
		pass

	def msg(self, msg):
		pass

_logger = _dummyLogger()
_curlevel = None

# public methods

def init(level):
	global _logger
	global _curlevel
	_setColored()
	_logger = _sysLogger(level)
	_curlevel = level

def levels():
	return ['debug', 'info', 'warn', 'msg', 'error', 'quiet']

def defaultLevel():
	return 'warn'

def debug(msg, depth = None, tag = None):
	_logger.debug(msg, depth = depth, tag = tag)

def error(msg):
	_logger.error(msg)

def warn(msg):
	_logger.warn(msg)

def info(msg):
	_logger.info(msg)

def msg(msg):
	_logger.msg(msg)
