# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path

from _sadm.deploy import extractor, self_extract

deployfn = path.join('tdata', 'build', 'envsetup', 'build.test.deploy')
rootdir = path.join('tdata', 'tmp', 'self_extract.test')

def test_extract(env_setup):
	env = env_setup(name = 'build.test', action = 'build')
	assert path.isfile(deployfn)
	assert self_extract._vars == {}
	assert self_extract._cargo == {}
	self_extract._vars = {
		'env': 'build.test',
		'rootdir': rootdir,
	}
	self_extract._cargo = extractor._getcargo(env,
		path.normpath(env.build.rootdir()))
	assert sorted(self_extract._cargo.keys()) == ['build.test.env', 'build.test.zip']
	dstdir = path.join(rootdir, 'env')
	assert not path.isdir(dstdir)
	self_extract.extract(dstdir)
	assert path.isdir(dstdir)
	assert path.isfile(path.join(dstdir, 'build.test.env'))
	assert path.isfile(path.join(dstdir, 'build.test.zip'))
