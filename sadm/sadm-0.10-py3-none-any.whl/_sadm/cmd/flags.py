# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import argparse

from _sadm import log, version

__all__ = ['new', 'parse']

def new(prog, desc = ''):
	p = argparse.ArgumentParser(prog = prog, description = desc)
	p.add_argument('-V', '--version', help = 'show version and exit',
		action = 'version', version = version.string())
	p.add_argument('--debug', help = 'enable debug settings',
		action = 'store_true', default = False)
	p.add_argument('--log', help = "set log level (%s)" % log.defaultLevel(),
		default = log.defaultLevel(), choices = log.levels())
	p.add_argument('--env', help = 'env name (default)',
		metavar = 'name', default = 'default')
	p.add_argument('--profile', help = 'profile name (default)',
		metavar = 'name', default = 'default')
	return p

def parse(p):
	args = p.parse_args()
	if args.debug:
		log.init('debug')
	else:
		log.init(args.log)
	log.debug("sadm version %s" % version.get())
	return args
