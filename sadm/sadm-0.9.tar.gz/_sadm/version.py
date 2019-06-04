# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

def get():
	try:
		from _sadm._version import version as build_version
		return build_version # pragma: no cover
	except ImportError:
		return 'master'

def string():
	return '%(prog)s version ' + get()
