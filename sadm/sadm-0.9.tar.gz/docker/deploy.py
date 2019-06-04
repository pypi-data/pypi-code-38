#!/usr/bin/env python3

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys

from compileall import compile_dir
from os import path, getenv
from subprocess import call

loglevel = getenv('SADM_LOG', 'warn')

from _sadm import log, env

if __name__ == '__main__':
	compile_dir('./_sadm', quiet = 1) # avoid root owned .pyc files
	log.init(loglevel)
	pname = sys.argv[1]
	deployfn = "./docker/build/devel/%s.deploy" % pname
	if not path.isfile(deployfn):
		rc, _ = env.run('devel', pname, 'build', cfgfile = './docker/sadm.cfg')
		if rc != 0:
			sys.exit(rc)
	sys.exit(call("./docker/run.sh %s" % deployfn, shell = True))
