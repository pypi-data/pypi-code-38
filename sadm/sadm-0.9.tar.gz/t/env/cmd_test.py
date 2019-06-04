# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, unlink
from pytest import raises

from _sadm.env import cmd
from _sadm.errors import EnvError, PluginError

def test_run(env_setup):
	env = env_setup()
	cfgfn = path.join('tdata', 'build', 'envsetup', 'testing.meta', 'configure.ini')
	sessfn = path.join('tdata', 'build', 'envsetup', 'testing.meta', 'session.json')
	for fn in (cfgfn, sessfn):
		if path.isfile(fn):
			unlink(fn)
	assert not path.isfile(cfgfn)
	assert not path.isfile(sessfn)
	cmd.run(env, 'build')
	assert path.isfile(cfgfn)
	assert path.isfile(sessfn)

def test_run_invalid_action(testing_env):
	env = testing_env()
	with raises(EnvError, match = 'invalid action configure'):
		cmd.run(env, 'configure')

def test_plugin_no_action(testing_env):
	env = testing_env()
	env.configure()
	with raises(PluginError, match = 'testing plugin no action nocmd'):
		cmd._runAction(env, 'build', cmd = 'nocmd', force = True)
