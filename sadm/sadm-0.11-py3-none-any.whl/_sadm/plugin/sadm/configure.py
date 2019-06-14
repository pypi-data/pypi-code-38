# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import version

def configure(env, cfg):
	s = env.settings
	s.set('sadm', 'env', env.name())
	s.set('sadm', 'profile', env.profile())
	sess = env.session
	sess.set('sadm.version', version.get())
