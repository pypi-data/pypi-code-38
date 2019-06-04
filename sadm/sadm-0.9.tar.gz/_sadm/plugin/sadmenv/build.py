# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import json

from hashlib import sha256
from os import path
from shutil import make_archive

from _sadm.plugin.utils import builddir

__all__ = ['pre_build', 'post_build']

_destdir = path.join(path.sep, 'opt', 'sadm')

def pre_build(env):
	env.build.create()

def post_build(env):
	env.build.close()
	_checksum(env)
	_meta(env)
	_zip(env)

def _checksum(env):
	env.log("%s.tar" % env.name())
	fn = builddir.fpath(env, env.name() + '.tar', meta = True)
	h = sha256()
	with open(fn, 'rb') as fh:
		h.update(fh.read())
	env.session.set('sadm.env.checksum', h.hexdigest())

def _zip(env):
	env.log("%s.zip" % env.name())
	rdir = builddir.fpath(env, '.', meta = True)
	fn = builddir.fpath(env, '.')
	make_archive(fn, 'zip', root_dir = rdir, base_dir = '.', verbose = 1)
	h = sha256()
	with open(fn + '.zip', 'rb') as fh:
		h.update(fh.read())
	with open(fn + '.env', 'x') as fh:
		fh.write("%s  %s\n" % (h.hexdigest(),
			path.join(_destdir, 'env', env.name() + '.zip')))

def _meta(env):
	env.log('meta.json')
	with builddir.create(env, 'meta.json', meta = True) as fh:
		json.dump(_getmeta(env), fh, indent = '\t', sort_keys = True)

def _getmeta(env):
	return {
		'sadm.env.name': env.name(),
		'sadm.env.profile': env.profile(),
		'sadm.env.checksum': env.session.get('sadm.env.checksum'),
		'sadm.configure.checksum': env.session.get('sadm.configure.checksum'),
		'sadm.version': env.session.get('sadm.version'),
	}
