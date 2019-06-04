# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import getenv
from io import StringIO
from bottle import route, view

from _sadm import log, cfg
from _sadm.web import tpl

@route('/')
@view('index.html')
@tpl.data('home')
def index():
	log.debug("index")
	config = cfg.new()
	return {
		'cfgfile': config.filename(),
		'cfg': _getCfg(config),
		'user': getenv('USER', 'nouser'),
	}

def _getCfg(config):
	buf = StringIO()
	config.reload()
	config.write(buf)
	buf.seek(0, 0)
	return buf.read()
