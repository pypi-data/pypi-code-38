# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import environ

from _sadm.plugin.utils.cmd import call, call_check

from .check import check

__all__ = ['deploy']

_cmdenv = environ.copy()
_cmdenv['DEBIAN_FRONTEND'] = 'noninteractive'

def deploy(env):
	if env.settings.getboolean('os.pkg', 'update'):
		env.log('update')
		_update()
	for diff in check(env, action = 'remove'):
		opt, pkg = diff
		env.log("%s %s" % (opt, pkg))
		_remove(pkg)
	for diff in check(env, action = 'install'):
		opt, pkg = diff
		env.log("%s %s" % (opt, pkg))
		_install(pkg)
	for diff in check(env, action = 'prune'):
		opt, pkg = diff
		env.log("%s %s" % (opt, pkg))
		_prune(pkg)

def _call(cmd):
	call_check(cmd, env = _cmdenv)

def _update():
	_call(['apt-get', 'update'])

def _remove(pkg):
	_call(['apt-get', 'autoremove', '-yy', '--purge', pkg])

def _install(pkg):
	_call(['apt-get', 'install', '-yy', '--purge', '--no-install-recommends', pkg])

def _prune(pkg):
	_call(['apt-get', 'autoremove', '-yy', '--purge', pkg])
