# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from importlib import import_module
from pytest import raises

from _sadm import configure
from _sadm.errors import PluginError

def test_register_error():
	with raises(RuntimeError, match = 'plugin testing already registered'):
		configure.register('testing', 'filename')

def test_get_plugin():
	p = configure.getPlugin('testing', 'configure')
	assert p.mod == import_module('_sadm.plugin.testing.configure')

def test_get_plugin_error():
	with raises(PluginError, match = 'noplugin plugin not found'):
		configure.getPlugin('noplugin', 'configure')
	with raises(PluginError, match = 'testing.nomod: No module named'):
		configure.getPlugin('testing', 'nomod')
