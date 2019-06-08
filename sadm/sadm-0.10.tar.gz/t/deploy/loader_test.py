# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path

from _sadm.deploy import loader

envfn = path.join('tdata', 'build', 'envsetup', 'build.test.env')
tarfn = path.join('tdata', 'build', 'deploy', 'build.test', 'build.test.tar')
inifn = path.join('tdata', 'build', 'deploy', 'build.test', 'configure.ini')
metafn = path.join('tdata', 'build', 'deploy', 'build.test', 'meta.json')

def test_importenv(env_setup):
	env = env_setup(name = 'build.test', action = 'build')
	assert path.isfile(envfn)
	assert not path.isdir(path.dirname(tarfn))
	loader._importenv(envfn)
	assert path.isfile(tarfn)
	assert path.isfile(inifn)
	assert path.isfile(metafn)
