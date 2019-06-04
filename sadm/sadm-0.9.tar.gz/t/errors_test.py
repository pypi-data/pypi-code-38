# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.errors import Error

def test_error():
	err = Error('errMsg')
	err.typ = 'errType'
	assert str(err) == 'errType: errMsg'
	assert repr(err) == '<sadm.errType: errMsg>'
	err2 = Error('errMsg')
	err2.typ = 'errType'
	assert err == err2
	err2.typ = 'errType2'
	assert err != err2
