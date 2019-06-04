# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from pytest import raises
from os import path, unlink, makedirs
from time import time

from _sadm import asset
from _sadm.env import Env, _lock, _unlock
from _sadm.env import cmd as envcmd
from _sadm.env import run as envrun
from _sadm.env.profile import Profile
from _sadm.env.settings import Settings
from _sadm.errors import EnvError, AssetNotFoundError, SessionError

def test_env(testing_env):
	e = testing_env()
	assert isinstance(e, Env)
	assert e.name() == 'testing'
	assert e.profile() == 'testing'
	assert e.cfgfile() == path.join('testing', 'config.ini')
	assert isinstance(e._profile, Profile)
	assert e._profile.name() == 'testing'
	assert isinstance(e.assets, asset.Manager)
	assert isinstance(e.settings, Settings)

def test_env_configure(testing_env):
	e = testing_env()
	assert isinstance(e.settings, Settings)
	with raises(AssetNotFoundError, match = 'No such file or directory'):
		e._cfgfile = 'noconfig.ini'
		e.configure()

def test_env_error(testing_env):
	with raises(EnvError, match = 'env not found'):
		Env('testing', 'noenv')

def test_load_error(testing_env):
	e = testing_env()
	with raises(EnvError, match = 'config file not set'):
		e._load(fn = '')
	with raises(EnvError, match = 'noprofile.dir directory not found'):
		e._load(pdir = 'tdata/noprofile.dir')
	with raises(EnvError, match = 'profile-dir-isfile.test is not a directory'):
		e._load(pdir = 'tdata/profile-dir-isfile.test')

def test_start_end_action(testing_env):
	e = testing_env()
	assert [n for n in e._run.keys()] == []
	e.start('testing_action')
	assert [n for n in e._run.keys()] == ['testing_action']
	assert e._run['testing_action'].get('start', '') != ''
	assert e._run['testing_action'].get('tag.prev', None) is not None
	assert e._run['testing_action'].get('end', None) is None
	e.end('testing_action')
	assert e._run['testing_action'].get('end', '') != ''

def test_start_end_error(testing_env):
	e = testing_env()
	assert [n for n in e._run.keys()] == []
	e.start('testing_error')
	with raises(EnvError, match = 'testing_error action already started'):
		e.start('testing_error')
	assert [n for n in e._run.keys()] == ['testing_error']
	with raises(EnvError, match = 'testing_end_error action was not started'):
		e.end('testing_end_error')

def test_report(testing_env):
	e = testing_env()
	e.start('action1')
	e.end('action1')
	e.report('testing_report')
	e.report('testing_report', startTime = time() - 10)
	e.start('action2')
	with raises(EnvError, match = 'not finished action\(s\): action2'):
		e.report('testing_report')

def test_lock(testing_env):
	fn = path.join('tdata', 'testing', '.lock')
	e = testing_env()
	with e.lock():
		assert e._lockfn.endswith(fn)
		assert path.isfile(fn)
	assert not path.isfile(fn)
	assert e._lockfn is None

def test_lock_error(testing_env):
	fn = path.join('tdata', 'testing', '.lock')
	e = testing_env()
	_lock(e)
	assert path.isfile(fn)
	with raises(EnvError, match = 'lock file exists:'):
		_lock(e)
	_unlock(e)
	assert not path.isfile(fn)

def test_unlock_error(testing_env):
	fn = path.join('tdata', 'testing', '.lock')
	e = testing_env()
	_lock(e)
	assert path.isfile(fn)
	assert e._lockfn is not None
	_unlock(e)
	assert not path.isfile(fn)
	assert e._lockfn is None
	_unlock(e)
	assert e._lockfn is None
	e._lockfn = fn
	e.session.start()
	with raises(EnvError, match = 'unlock file not found:'):
		_unlock(e)
	assert not path.isfile(fn)

def test_env_nodir_error():
	rc, _ = envrun('testing', 'testing.nodir', 'build')
	assert rc == 1

def test_run():
	cfgfn = path.join('tdata', 'build', 'envsetup', 'testing.meta', 'configure.ini')
	if path.isfile(cfgfn):
		unlink(cfgfn)
	assert not path.isfile(cfgfn)
	rc, _ = envrun('envsetup', 'testing', 'build')
	assert rc == 0
	assert path.isfile(cfgfn)
	unlink(cfgfn)

def test_run_env_error():
	cfgfn = path.join('tdata', 'build', 'envsetup', 'testing.meta', 'configure.ini')
	if path.isfile(cfgfn):
		unlink(cfgfn)
	assert not path.isfile(cfgfn)
	rc, err = envrun('envsetup', 'testing', 'configure')
	assert err == EnvError
	assert rc == 1
	assert not path.isfile(cfgfn)

def test_run_error():
	lockfn = path.join('tdata', 'build', 'envsetup', 'testing.errors.lock')
	if path.isfile(lockfn):
		unlink(lockfn)
	rc, err = envrun('envsetup', 'testing.errors', 'build')
	assert err == SessionError
	assert rc == 2

def test_envsetup(env_setup):
	env = env_setup(configure = True)
	assert env.name() == 'testing'
	assert env.profile() == 'envsetup'
	assert env.session._start is not None # env.configure() was run

def test_envsetup_action(env_setup):
	mdir = path.join('tdata', 'build', 'envsetup', 'testing')
	zfn = path.join('tdata', 'build', 'envsetup', 'testing.zip')
	assert not path.isdir(mdir)
	assert not path.isfile(zfn)
	env_setup(action = 'build')
	assert path.isdir(mdir)
	assert path.isfile(zfn)
	with raises(EnvError, match = 'invalid action configure'):
		env_setup(action = 'configure')
	assert not path.isdir(mdir)

def test_env_default(testing_env):
	e = testing_env(name = 'default', profile = 'default')
	assert e.name() == 'testing'
	assert e.profile() == 'testing'
