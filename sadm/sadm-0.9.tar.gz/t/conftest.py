# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import pytest
from os import path, makedirs, unlink
from shutil import rmtree

# logger

from _sadm import log
log._colored = False
log.init('quiet')

# remove version autogen module

_versionfn = path.join('_sadm', '_version.py')
if path.isfile(_versionfn):
	unlink(_versionfn)

# register testing plugin

import _sadm.plugin.testing

# config

from _sadm import cfg
cfg._cfgFile = path.join('tdata', 'sadm.cfg')

# testing profile

from _sadm.env import profile

@pytest.fixture
def testing_profile():
	def wrapper(name = 'testing'):
		return profile.Profile(name)
	return wrapper

# testing env

from _sadm import env

@pytest.fixture
def testing_env():
	def wrapper(name = 'testing', profile = 'testing'):
		e = env.Env(profile, name)
		_cleanEnv(e)
		return e
	return wrapper

# testing settings

@pytest.fixture
def testing_settings():
	envmod = env
	def wrapper(profile = 'testing', env = 'testing', cfgfile = None):
		if cfgfile is not None:
			cfgfile = path.join(profile, cfgfile)
		e = envmod.Env(profile, env)
		_cleanEnv(e)
		e.configure(cfgfile = cfgfile)
		return e.settings
	return wrapper

# testing env setup

from _sadm.env import cmd as envcmd

@pytest.fixture
def env_setup():
	def wrapper(name = 'testing', profile = 'envsetup', configure = False,
		cfgfile = None, action = None, mkdirs = False):
		if action is not None:
			# configure is called from cmd.run
			configure = False
		e = env.Env(profile, name)
		_cleanEnv(e, mkdirs = mkdirs)
		if configure:
			e.configure(cfgfile = cfgfile)
		if action is not None:
			envcmd.run(e, action)
		return e
	return wrapper

def _cleanEnv(env, mkdirs = False):
	tmpdir = path.join('tdata', 'tmp')
	bdir = path.normpath(env.build.rootdir())
	pdir = path.realpath(path.join('tdata', env.profile(), env.name()))
	deploydir = path.join(path.dirname(path.dirname(bdir)), 'deploy', env.name())
	_dirs = (
		tmpdir,
		bdir,
		bdir + '.meta',
		deploydir,
	)
	for d in _dirs:
		if path.isdir(d):
			rmtree(d)
	_files = (
		bdir + '.zip',
		bdir + '.env',
		bdir + '.env.asc',
		bdir + '.deploy',
		path.join(bdir, '.lock'),
		path.join(pdir, '.lock'),
	)
	for f in _files:
		if path.isfile(f):
			unlink(f)
	if mkdirs:
		for d in _dirs:
			makedirs(d)
	else:
		makedirs(tmpdir)
