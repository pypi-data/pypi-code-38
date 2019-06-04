# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log, cfg
from _sadm.errors import ProfileError

__all__ = ['Profile']

class Profile(object):
	_name = None

	def __init__(self, name, config = None):
		log.debug("profile init %s" % name)
		if config is None:
			config = cfg.new()
		self._name = name
		self._load(config)

	def _load(self, config):
		log.debug("load %s" % self._name)
		if not config.has_section(self._name):
			log.debug("%s profile not found" % self._name)
			raise ProfileError("%s profile not found" % self._name)

	def name(self):
		return self._name
