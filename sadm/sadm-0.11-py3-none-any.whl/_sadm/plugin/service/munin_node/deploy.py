# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import unlink, write, close
from tempfile import mkstemp

from _sadm.plugin.utils.cmd import call, call_check

__all__ = ['deploy']

def deploy(env):
	_autoconf(env)
	call_check('service munin-node stop')
	call_check('service munin-node start')
	call_check('service munin-node status')

def _autoconf(env):
	env.log('autoconf')
	tmpfn = ''
	fd, tmpfn = mkstemp(prefix = __name__, text = True)
	write(fd, b'exit 0')
	close(fd)
	env.debug("tmpfn %s" % tmpfn)
	call("munin-node-configure --shell >%s 2>&1" % tmpfn)
	call_check("/bin/sh -eu %s" % tmpfn)
	unlink(tmpfn)
