# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle

from _sadm import log, libdir

_staticdir = libdir.path('web', 'static')

@bottle.route('/static/<filename:path>')
def _static(filename):
	return bottle.static_file(filename, root = _staticdir, download = False)

# load views
import _sadm.web.errors
import _sadm.web.view.home
import _sadm.web.view.profile
import _sadm.web.view.syslog
import _sadm.web.view.about

def start(host, port, debug):
	htmldir = libdir.path('web', 'html')
	log.debug("start %s" % htmldir)
	bottle.TEMPLATE_PATH = [htmldir]
	bottle.run(host = host, port = port, reloader = debug,
		quiet = log._curlevel != 'debug', debug = debug)
