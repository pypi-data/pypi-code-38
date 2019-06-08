# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path
from pytest import raises

from _sadm import build
from _sadm.errors import BuildError

rootdir = path.join('tdata', 'build', 'envsetup')
builddir = path.join(rootdir, 'build.test')
tarfn = path.join(rootdir, 'build.test.meta', 'build.test.tar')
assetfn = path.join(builddir, 'asset.file')

def build_assets():
	with open(assetfn, 'x') as fh:
		fh.write('testing')

def test_create(env_setup):
	env_setup('build.test', mkdirs = True)
	m = build.Manager(builddir)
	assert not path.isfile(tarfn)
	m.create()
	assert not path.isfile(tarfn)
	assert len(m._data) == 0
	m.close()
	assert path.isfile(tarfn)

def test_create_error(env_setup):
	env_setup('build.test', mkdirs = True)
	m = build.Manager(builddir)
	assert not path.isfile(tarfn)
	with open(tarfn, 'x') as fh:
		fh.write('1')
	assert path.isfile(tarfn)
	with raises(BuildError, match = "%s file exists" % tarfn):
		m.create()

def test_data(env_setup):
	env_setup('build.test', mkdirs = True)
	m = build.Manager(builddir)
	m.create()
	assert len(m._data) == 0
	build_assets()
	m.addfile('asset.file')
	assert len(m._data) == 1
	m.close()

def test_dir_data(env_setup):
	env_setup('build.test', mkdirs = True)
	m = build.Manager(builddir)
	m.create()
	assert len(m._data) == 0
	build_assets()
	m.adddir('.')
	assert len(m._data) == 1
	m.close()
