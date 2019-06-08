# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque, namedtuple
from importlib import import_module
from os import path

from _sadm import log, dist
from _sadm.errors import PluginError

__all__ = ['register', 'getPlugin', 'pluginList']

_reg = {}
_order = deque()

Plugin = namedtuple('Plugin', ('name', 'fullname', 'config', 'meta', 'mod'))

def register(name, filename):
	global _next
	n = name.replace('_sadm.plugin.', '')
	if _reg.get(n, None) is not None:
		raise RuntimeError("plugin %s already registered" % name)
	srcdir = path.realpath(path.dirname(filename))
	cfgfn = path.join(srcdir, 'config.ini')
	metafn = path.join(srcdir, 'meta.json')
	_reg[n] = {
		'name': name,
		'distname': _distname(srcdir, name),
		'config': cfgfn,
		'meta': metafn,
	}
	_order.append(n)

def _distname(srcdir, name):
	dn = dist.getname()
	if path.isfile(path.join(srcdir, dn, '__init__.py')):
		return '.'.join([name, dn])
	return ''

def pluginsList(revert = False):
	if revert:
		for p in reversed(_order):
			yield p
	else:
		for p in _order:
			yield p

def getPlugin(name, action):
	p = _reg.get(name, None)
	if p is None:
		raise PluginError("%s plugin not found" % name)
	pkg = p['name']
	if action == 'deploy' and p['distname'] != '':
		pkg = p['distname']
	try:
		mod = import_module("%s.%s" % (pkg, action))
	except ImportError as err:
		log.debug("%s: %s" % (type(err), err))
		raise PluginError("%s.%s: %s" % (name, action, err))
	except Exception as err:
		raise PluginError("%s %s: %s" % (name, action, err))
	return Plugin(name = name, fullname = pkg, config = p['config'],
		meta = p['meta'], mod = mod)
