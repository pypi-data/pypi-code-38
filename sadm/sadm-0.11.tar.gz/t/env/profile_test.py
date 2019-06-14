# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from pytest import raises
from _sadm.errors import Error
from _sadm.env.profile import Profile

def test_profile(testing_profile):
	p = testing_profile()
	assert p.name() == 'testing'

def test_profileError():
	with raises(Error, match = 'ProfileError: noname profile not found'):
		Profile('noname')
