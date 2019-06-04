# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from datetime import datetime
from _sadm import log, version

_viewreg = {}

def data(view):
	if _viewreg.get(view, False):
		raise RuntimeError("%s view already registered" % view)
	_viewreg[view] = True
	def wrapper(func):
		def decorator(*args, **kwargs):
			_start = datetime.timestamp(datetime.now())
			return _tplData(view, func(*args, **kwargs), _start)
		return decorator
	return wrapper

def _tplData(view, d, _start):
	log.debug("view data %s" % view)
	d['view'] = view
	d['version'] = version.get()
	d['now'] = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
	d['took'] = "%.5f" % (datetime.timestamp(datetime.now()) - _start)
	return d
