# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path
from subprocess import call

from _sadm import cfg

trun = path.join('.', 'docker', 'trun.py')

def test_devel_envs():
	config = cfg.new(cfgfile = path.join('docker', 'sadm.cfg'))
	for env in config.listEnvs('devel'):
		rc = call([trun, env])
		assert rc == 0, "%s %s failed: %d" % (trun, env, rc)
