# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path
from _sadm.plugin.utils import builddir

__all__ = ['build']

def build(env):
	homedir = env.settings.get('os', 'users.home.dir')
	env.debug("home dir %s" % homedir)
	for user in env.settings['os.user']:
		uid = env.settings.getint('os.user', user)
		# ~ env.log("%d %s" % (uid, user))
		_synchome(env, user, homedir)

def _synchome(env, user, homedir):
	cfgdir = env.settings.get('os', 'users.config.dir')
	dirmode = env.settings.getint('os', 'users.dirmode')
	filemode = env.settings.getint('os', 'users.filemode')
	srcdir = path.join(cfgdir, user)
	dstdir = path.join(homedir, user)
	if env.assets.isdir(cfgdir, user):
		env.log("sync %s -> %s" % (srcdir, dstdir))
		builddir.sync(env, srcdir, dstdir, user = user, group = user,
			dirmode = dirmode, filemode = filemode)
