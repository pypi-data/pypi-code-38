# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from io import StringIO
from pytest import raises

from _sadm.errors import SessionError
from _sadm.env.session import Session

def test_session():
	sess = Session()
	assert isinstance(sess._d, dict)
	assert sess._start is None
	sess.start()
	assert sess._start is not None
	took = sess.stop()
	assert sess._start is None
	assert isinstance(took, float)

def test_start_error():
	sess = Session()
	sess.start()
	with raises(SessionError, match = 'session already started'):
		sess.start()

def test_stop_error():
	sess = Session()
	sess.start()
	sess.stop()
	sess._done = False
	with raises(SessionError, match = 'session not started'):
		sess.stop()

def test_set_get():
	sess = Session()
	sess.start()
	sess.set('test', 'testing')
	assert sess.get('test') == 'testing'
	sess.stop()

def test_get_default():
	sess = Session()
	sess.start()
	assert sess.get('test', 'testing_default') == 'testing_default'
	sess.stop()

def test_set_get_error():
	sess = Session()
	sess.start()
	with raises(SessionError, match = 'test option not set'):
		assert sess.get('test') == 'testing'
	sess.set('test', 'testing')
	with raises(SessionError, match = 'test option already set'):
		sess.set('test', 'testing')
	sess.stop()

def test_dump():
	sess = Session()
	sess.start()
	fh = StringIO()
	sess.dump(fh, indent = None)
	fh.seek(0, 0)
	assert fh.read() == '{}'
	fh.truncate()
	fh.seek(0, 0)
	sess.set('opt1', 'val1')
	sess.set('opt2', 'val2')
	sess.dump(fh, indent = None)
	fh.seek(0, 0)
	assert fh.read() == '{"opt1": "val1", "opt2": "val2"}'
	sess.stop()

def test_stopped_error():
	sess = Session()
	sess.start()
	sess.stop()
	with raises(SessionError, match = 'session stopped'):
		sess.set('testing', 'stopped')
