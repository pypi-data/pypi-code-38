# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.web import tpl

def test_loaded():
	assert tpl._viewreg == {
		'home': True,
		'profile': True,
		'syslog': True,
		'about': True,
		'err500': True,
		'err400': True,
	}, 'missing view'
