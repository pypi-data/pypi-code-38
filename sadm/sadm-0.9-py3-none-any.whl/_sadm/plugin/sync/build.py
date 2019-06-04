# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.plugin.utils import builddir

__all__ = ['build']

def build(env):
	for inf in env.session.get('sync'):
		src = inf['src']
		dst = inf['dst']
		if env.assets.isdir(src):
			builddir.sync(env, src, dst)
		else:
			with env.assets.open(src) as sfh:
				with builddir.create(env, dst) as dfh:
					dfh.write(sfh.read())
