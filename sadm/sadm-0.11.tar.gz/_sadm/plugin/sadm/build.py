# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from hashlib import sha256
from os import path
from subprocess import call

from _sadm.deploy import extractor
from _sadm.errors import BuildError
from _sadm.plugin.utils import builddir

__all__ = ['pre_build', 'post_build']

def pre_build(env):
	builddir.lock(env)
	_writeSettings(env)

def post_build(env):
	_saveSession(env)
	_signBuild(env)
	extractor.gen(env)
	builddir.unlock(env)

def _saveSession(env):
	env.debug('session.json')
	with builddir.create(env, 'session.json', meta = True) as fh:
		env.session.dump(fh)

def _writeSettings(env):
	env.log('configure.ini')
	fn = None
	with builddir.create(env, 'configure.ini', meta = True) as fh:
		env.settings.write(fh)
		fn = fh.name
	h = sha256()
	with open(fn, 'rb') as fh:
		h.update(fh.read())
	env.session.set('sadm.configure.checksum', h.hexdigest())

def _signBuild(env):
	sid = env.config.get(env.profile(), 'build.sign', fallback = '')
	sid = sid.strip()
	if sid != '':
		env.log("sign id %s" % sid)
		fn = path.normpath(env.build.rootdir()) + '.env'
		env.log("sign env %s" % fn)
		rc = call("gpg --no-tty --yes -u '%s' -sba %s" % (sid, fn), shell = True)
		if rc != 0:
			raise BuildError('build sign using gpg failed')
