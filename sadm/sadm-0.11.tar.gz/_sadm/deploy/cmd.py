# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log, env, deploy

def run(envname):
	log.debug("run %s" % envname)
	rc, _ = env.run('deploy', envname, 'deploy', cfgfile = deploy.cfgfile)
	return rc
