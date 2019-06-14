# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path

from _sadm.plugin.utils import builddir

__all__ = ['build']

def build(env):
	jaildir = env.assets.name(env.settings.get('network.fail2ban', 'jail.dir'))
	destdir = env.settings.get('network.fail2ban', 'jail.destdir')
	jenable = env.settings.getlist('network.fail2ban', 'jail.enable')
	if env.assets.isdir(jaildir):
		for jn in jenable:
			src = env.assets.name(jaildir, jn + '.conf')
			dst = path.join(destdir, jn + '.conf')
			env.log("%s" % dst)
			builddir.copy(env, src, dst)
