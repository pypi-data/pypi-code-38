#!/usr/bin/env python3

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys
from subprocess import call

if __name__ == '__main__':
	pname = sys.argv[1]
	deployfn = "./docker/build/devel/%s.deploy" % pname
	sys.exit(call("./docker/run.sh %s" % deployfn, shell = True))
