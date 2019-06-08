# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from pytest import raises

from _sadm import libdir
from _sadm.errors import PluginError, PluginScriptNotFound, PluginScriptNoExec
from _sadm.errors import PluginScriptTimeout
from _sadm.plugin.utils import scripts

s = scripts.Scripts('testing', distname = 'testing')

def test_scripts_dir():
	assert s._dir == libdir.path('scripts', 'testing', 'testing')

def test_noscript():
	spath = libdir.path('scripts', 'testing', 'testing', 'noscript.sh')
	with raises(PluginScriptNotFound, match = "PluginScriptNotFound: %s" % spath) as err:
		s.run('noscript.sh')
	assert err.errisinstance(PluginError)

def test_run():
	rc = s.run('testing.sh')
	assert rc == 0

def test_run_error():
	rc = s.run('testing-error.sh')
	assert rc == 1

def test_run_noexec():
	spath = libdir.path('scripts', 'testing', 'testing', 'testing-noexec.sh')
	with raises(PluginScriptNoExec, match = "PluginScriptNoExec: %s" % spath) as err:
		s.run('testing-noexec.sh')
	assert err.errisinstance(PluginError)

def test_timeout():
	spath = libdir.path('scripts', 'testing', 'testing', 'testing-timeout.sh')
	prevttl = scripts._TTL
	scripts._TTL = 0.2
	with raises(PluginScriptTimeout,
		match = "PluginScriptTimeout: %s after 0.2 seconds" % spath) as err:
		s.run('testing-timeout.sh', '1')
	assert err.errisinstance(PluginError)
	scripts._TTL = prevttl

def test_run_args():
	rc = s.run('testing-args.sh', ('1', '2', '3'))
	assert rc == 0
