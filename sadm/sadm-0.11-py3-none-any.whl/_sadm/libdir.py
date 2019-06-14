# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os.path import realpath, dirname, join, normpath, sep

__all__ = ['path', 'openfile']

_srcdir = realpath(dirname(__file__))

def path(*parts):
	n = join(*parts)
	n = normpath(n)
	while n.startswith(sep):
		n = n.replace(sep, '', 1)
	return join(_srcdir, n)

def openfile(*parts):
	return open(path(*parts), 'r', encoding = 'utf-8')
