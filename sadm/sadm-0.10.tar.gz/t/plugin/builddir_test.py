# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, unlink
from pytest import raises

from _sadm.errors import SessionError, EnvError
from _sadm.plugin.utils import builddir

def test_lock_unlock(env_setup):
	lockfn = path.join('tdata', 'build', 'envsetup', 'testing.lock')
	env = env_setup(configure = True)
	assert not path.isfile(lockfn)
	builddir.lock(env)
	assert path.isfile(lockfn)
	builddir.unlock(env)
	assert not path.isfile(lockfn)

def test_lock_error(env_setup):
	lockfn = path.join('tdata', 'build', 'envsetup', 'testing.lock')
	env = env_setup(configure = True)
	assert not path.isfile(lockfn)
	builddir.lock(env)
	with raises(SessionError, match = 'lockfn option already set'):
		builddir.lock(env)
	del env.session._d['lockfn']
	with raises(EnvError, match = 'lock file exists: '):
		builddir.lock(env)
	builddir.unlock(env)

def test_unlock_error(env_setup):
	lockfn = path.join('tdata', 'build', 'envsetup', 'testing.lock')
	if path.isfile(lockfn):
		unlink(lockfn)
	env = env_setup(configure = True)
	assert not path.isfile(lockfn)
	with raises(SessionError, match = 'lockfn option not set'):
		builddir.unlock(env)
	builddir.lock(env) # set session lockfn
	builddir.unlock(env)
	with raises(EnvError, match = 'unlock file not found'):
		builddir.unlock(env)

def test_fpath(env_setup):
	env = env_setup(configure = True)
	builddir.lock(env)
	try:
		p = path.join('tdata', 'build', 'envsetup', 'testing', 'p1', 'p2', 'p3')
		assert builddir.fpath(env, 'p1', 'p2', 'p3') == path.realpath(p)
	finally:
		builddir.unlock(env)

def test_fpath_relname(env_setup):
	env = env_setup(configure = True)
	builddir.lock(env)
	try:
		p = path.join('tdata', 'build', 'envsetup', 'testing', 'p1', 'p2', 'p3')
		assert builddir.fpath(env, path.sep + 'p1', 'p2', 'p3') == path.realpath(p)
	finally:
		builddir.unlock(env)

def test_fpath_meta(env_setup):
	env = env_setup(configure = True)
	builddir.lock(env)
	try:
		p = path.join('tdata', 'build', 'envsetup', 'testing.meta', 'p1')
		assert builddir.fpath(env, 'p1', meta = True) == path.realpath(p)
	finally:
		builddir.unlock(env)

def test_create(env_setup):
	env = env_setup(configure = True)
	builddir.lock(env)
	try:
		env.build.create()
		fn = path.join('tdata', 'build', 'envsetup', 'testing', 'file.test')
		assert not path.isfile(fn)
		with builddir.create(env, 'file.test') as fh:
			fh.write('1')
		assert path.isfile(fn)
	finally:
		env.build.close()
		builddir.unlock(env)

def test_cleandir(env_setup):
	env = env_setup(configure = True)
	builddir.lock(env)
	try:
		envfn = path.join('tdata', 'build', 'envsetup', 'testing.env')
		metadir = path.join('tdata', 'build', 'envsetup', 'testing.meta')
		assert path.isdir(metadir)
		assert not path.isfile(envfn)
		with open(envfn, 'x') as fh:
			fh.write('1')
		assert path.isfile(envfn)
		builddir._cleandir(env, env.build.rootdir())
		assert path.isdir(metadir)
		assert not path.isfile(envfn)
	finally:
		builddir.unlock(env)

def test_create_makedirs(env_setup):
	fn = path.join('asset', 'create.test')
	env = env_setup(name = 'build.test', action = 'build')
	assert not path.isdir(env.build.rootdir('asset'))
	with builddir.create(env, fn) as fh:
		fh.write('1')
	assert path.isfile(env.build.rootdir(fn))

def test_sync_error(env_setup):
	srcdir = 'nosrcdir'
	dstdir = path.join(path.sep, 'internal', 'path')
	env = env_setup(name = 'build.test', action = 'build')
	assert not path.isdir(env.build.rootdir('internal'))
	with raises(FileNotFoundError, match = "No such file or directory"):
		builddir.sync(env, srcdir, dstdir)

def test_sync(env_setup):
	srcdir = path.join('build.test', 'assets.sync')
	dstdir = path.join(path.sep, 'internal', 'path')
	env = env_setup(name = 'build.test', action = 'build')
	assert not path.isdir(env.build.rootdir('internal'))
	builddir.sync(env, srcdir, dstdir)
	assert path.isfile(env.build.rootdir(dstdir, 'file.test'))
