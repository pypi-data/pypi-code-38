# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import tarfile

from collections import deque, namedtuple
from os import path

from _sadm import asset
from _sadm.errors import BuildError

_Info = namedtuple('_Info', ('name', 'args', 'type'))

class Manager(asset.Manager):
	_tarfn = None
	_data = None

	def create(self):
		self._data = deque()
		rdir = self.rootdir()
		en = path.basename(rdir)
		mdir = path.normpath(rdir) + '.meta'
		self._tarfn = path.join(mdir, en + '.tar')
		# python 3.4 does not support 'x:' open mode
		# self._tar = tarfile.open(self._tarfn, 'x:')
		if path.isfile(self._tarfn):
			raise BuildError("%s file exists" % self._tarfn)

	def close(self):
		with tarfile.open(self._tarfn, 'w') as tar:
			for inf in self._data:
				if inf.type == 'dir':
					self._adddir(tar, inf)
					continue
				self._addfile(tar, inf)

	def _tarinfo(self, inf, user = 'root', group = '',
		filemode = 644, dirmode = 755):
		if group == '':
			group = user
		inf.mtime = 0 # reproducible builds
		inf.uid = 0
		inf.gid = 0
		inf.uname = user
		inf.gname = group
		if inf.isdir():
			inf.mode = int(str(dirmode), 8)
		else:
			inf.mode = int(str(filemode), 8)

	def addfile(self, name, **kwargs):
		self._data.append(_Info(name = name, args = kwargs, type = 'file'))

	def _addfile(self, tar, inf):
		def _filter(fi):
			self._tarinfo(fi, **inf.args)
			return fi
		arcname = self.name(inf.name)
		fn = path.join(self.rootdir(), arcname)
		tar.add(fn, arcname = arcname, recursive = False, filter = _filter)

	def adddir(self, name, **kwargs):
		self._data.append(_Info(name = name, args = kwargs, type = 'dir'))

	def _adddir(self, tar, inf):
		def _filter(fi):
			self._tarinfo(fi, **inf.args)
			return fi
		arcname = self.name(inf.name)
		dirpath = path.join(self.rootdir(), arcname)
		tar.add(dirpath, arcname = arcname, recursive = True, filter = _filter)
