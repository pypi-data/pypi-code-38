# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import configure

_expectPlugins = {
	0: 'testing',
	1: 'sadm',
	2: 'sadmenv',
	3: 'os',
	4: 'os.pkg',
	5: 'os.user',
	6: 'sync',
}

def test_plugins_list():
	idx = 0
	for p in configure.pluginsList():
		assert p == _expectPlugins[idx]
		idx += 1

def test_plugins_list_revert():
	idx = max(_expectPlugins.keys())
	for p in configure.pluginsList(revert = True):
		assert p == _expectPlugins[idx]
		idx -= 1

def test_plugins_new():
	known = {}
	for n in _expectPlugins.values():
		known[n] = True
	for p in configure.pluginsList():
		assert known.get(p, False), "new unknown plugin: %s" % p
