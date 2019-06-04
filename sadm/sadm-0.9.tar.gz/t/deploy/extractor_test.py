# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, unlink
from pytest import raises

from _sadm.deploy import extractor
from _sadm.errors import BuildError

extractorfn = path.join('tdata', 'build', 'envsetup', 'testing.deploy')
envfn = path.join('tdata', 'build', 'envsetup', 'testing.env')
zipenvfn = path.join('tdata', 'build', 'envsetup', 'testing.zip')

def test_gen(env_setup):
	env = env_setup(action = 'build')
	assert path.isfile(extractorfn)
	assert path.isfile(envfn)
	assert path.isfile(zipenvfn)

def test_gen_error(env_setup):
	env = env_setup(action = 'build')
	with raises(BuildError, match = "%s file exists" % extractorfn):
		extractor.gen(env)

def test_env_error(env_setup):
	env = env_setup(action = 'build')
	assert path.isfile(extractorfn)
	assert path.isfile(envfn)
	unlink(extractorfn)
	unlink(envfn)
	with raises(BuildError, match = "%s file not found" % envfn):
		extractor.gen(env)

def test_zipenv_error(env_setup):
	env = env_setup(action = 'build')
	assert path.isfile(extractorfn)
	assert path.isfile(zipenvfn)
	unlink(extractorfn)
	unlink(zipenvfn)
	with raises(BuildError, match = "%s file not found" % zipenvfn):
		extractor.gen(env)
