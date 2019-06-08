# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path

from _sadm.errors import AssetError, AssetNotFoundError

class Manager(object):
	_dir = None

	def __init__(self, rootdir = '.'):
		self._dir = path.realpath(path.normpath(rootdir))

	def rootdir(self, *parts):
		if len(parts) > 0:
			return self._path(*parts)
		return self._dir

	def name(self, *parts):
		relname = path.normpath(path.join(*parts))
		while relname.startswith(path.sep):
			relname = relname.replace(path.sep, '', 1)
		return relname

	def _path(self, name, *parts):
		return path.join(self._dir, self.name(name, *parts))

	def open(self, name, *parts):
		try:
			return open(self._path(name, *parts), 'r')
		except FileNotFoundError as err:
			raise AssetNotFoundError(str(err))
		except OSError as err:
			raise AssetError(str(err))

	def isdir(self, name, *parts):
		n = self._path(name, *parts)
		return path.exists(n) and path.isdir(n)

	def isfile(self, name, *parts):
		n = self._path(name, *parts)
		return path.exists(n) and path.isfile(n)
