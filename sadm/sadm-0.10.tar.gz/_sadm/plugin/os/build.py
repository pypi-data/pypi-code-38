# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, makedirs

from _sadm.plugin.utils import builddir

__all__ = ['build']

def build(env):
	_setHostname(env)

def _setHostname(env):
	hostname = env.settings.get('os', 'hostname')
	hfn = env.settings.get('os', 'hostname.file')
	env.debug("hostname file %s" % hfn)
	with builddir.create(env, hfn) as fh:
		fh.write(hostname.strip())
		fh.write('\n')
		fh.flush()
	env.log("%s: %s" % (hfn, hostname))
