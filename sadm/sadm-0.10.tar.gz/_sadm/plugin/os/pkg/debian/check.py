# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque

from _sadm import dist
from _sadm.plugin.utils.cmd import call

__all__ = ['check']

def check(env, action = None):
	diff = deque()
	dn = dist.getname()
	l = ('install', 'remove', 'prune')
	if action is not None and action in l:
		l = (action,)
	for opt in env.settings['os.pkg']:
		if opt in l:
			_check(env, opt, diff)
			continue
		if opt.startswith(dn + '.'):
			for n in l:
				if opt.endswith('.' + n):
					_check(env, opt, diff)
	return diff

def _check(env, opt, diff):
	l = []
	act = None

	if opt == 'remove' or opt.endswith('.remove'):
		act = 'remove'
		l = env.settings.getlist('os.pkg', opt)

	elif opt == 'install' or opt.endswith('.install'):
		act = 'install'
		l = env.settings.getlist('os.pkg', opt)

	elif opt == 'prune' or opt.endswith('.prune'):
		act = 'prune'
		l = env.settings.getlist('os.pkg', opt)

	for pkg in l:

		if act == 'remove':
			rc = call("/usr/bin/dpkg-query -s %s >/dev/null 2>/dev/null" % pkg)
			if rc == 0:
				diff.append((opt, pkg))
			elif rc > 1:
				raise env.error("os.pkg debian dpkg-query -s failed (rc:%d)" % rc)

		elif act == 'install':
			rc = call("/usr/bin/dpkg-query -s %s >/dev/null 2>/dev/null" % pkg)
			if rc == 1:
				diff.append((opt, pkg))
			elif rc > 1:
				raise env.error("os.pkg debian dpkg-query -s failed (rc:%d)" % rc)

		elif act == 'prune':
			rc = call("/usr/bin/dpkg-query -s %s >/dev/null 2>/dev/null" % pkg)
			if rc == 0:
				diff.append((opt, pkg))
			elif rc > 1:
				raise env.error("os.pkg debian dpkg-query -s failed (rc:%d)" % rc)
