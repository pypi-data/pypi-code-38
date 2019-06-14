#!/usr/bin/env python3

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys

from compileall import compile_dir
from os import getenv
from subprocess import call

loglevel = getenv('SADM_LOG', 'warn')

from _sadm import log, env

if __name__ == '__main__':
	compile_dir('./_sadm', quiet = 1) # avoid root owned __pycache__ dirs
	log.init(loglevel)
	pname = sys.argv[1]
	rc, _ = env.run('devel', pname, 'build', cfgfile = './docker/sadm.cfg')
	sys.exit(rc)
