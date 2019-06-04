# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import error, view
from _sadm import log
from _sadm.web import tpl

@error(500)
@view('error.html')
@tpl.data('err500')
def err500(err):
	log.debug("error type %s" % type(err))
	log.debug("%s - %s" % (err.status_line, err.exception))
	return {
		'err': err,
	}

@error(404)
@view('error.html')
@tpl.data('err400')
def err400(err):
	log.debug(err.status_line)
	return {
		'err': err,
	}
