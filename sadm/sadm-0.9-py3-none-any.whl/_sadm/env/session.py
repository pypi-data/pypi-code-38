# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import json
from time import time

from _sadm.errors import SessionError

__all__ = ['Session']

class Session(object):
	_start = None
	_done = False
	_d = None

	def __init__(self):
		self._d = {}

	def start(self):
		if self._start is not None:
			raise SessionError('session already started')
		self._start = time()
		self._done = False

	def _check(self):
		if self._done:
			raise SessionError('session stopped')
		if self._start is None:
			raise SessionError('session not started')

	def stop(self):
		self._check()
		took = time() - self._start
		del self._start
		self._done = True
		return took

	def set(self, opt, val):
		self._check()
		if self._d.get(opt, None) is not None:
			raise SessionError("%s option already set" % opt)
		self._d[opt] = val

	def get(self, opt, default = None):
		self._check()
		if self._d.get(opt, None) is None:
			if default is None:
				raise SessionError("%s option not set" % opt)
			else:
				return default
		return self._d[opt]

	def dump(self, fh, indent = '\t', sort_keys = True):
		self._check()
		json.dump(self._d, fh, indent = indent, sort_keys = sort_keys)
