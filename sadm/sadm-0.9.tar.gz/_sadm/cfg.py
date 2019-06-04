# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path
from configparser import ConfigParser

from _sadm import log
from _sadm.errors import ProfileError

__all__ = ['Config', 'new']

_cfgFile = path.realpath(path.join('.', 'sadm.cfg'))

_enablePlugins = [
	'sadm',
	'sadmenv',
]

_DEFAULT = {
	'name': '',
	'profile': 'default',
	'env': 'default',
	'dir': '.',
	'plugins': ','.join(_enablePlugins),
}

class Config(ConfigParser):
	_fn = None
	_name = None

	def _init(self, cfgfile = None):
		if cfgfile is None:
			cfgfile = _cfgFile
		self._fn = cfgfile
		log.debug("cfg init %s" % self._fn)
		self.reload()
		n = self.get('default', 'name')
		self._name = n.strip()
		if self._name == '':
			self._name = self._getName()

	def _getName(self):
		return path.basename(path.dirname(self._fn)).strip()

	def name(self):
		return self._name

	def filename(self):
		return self._fn

	def reload(self):
		try:
			with open(self._fn, 'r') as fh:
				self.read_file(fh)
		except FileNotFoundError:
			raise ProfileError("%s file not found" % self._fn)

	def listProfiles(self):
		return sorted(self.sections())

	def listEnvs(self, profile):
		if not self.has_section(profile):
			raise ProfileError("config profile %s not found" % profile)
		e = {}
		for opt in self.options(profile):
			if opt.startswith('env.'):
				n = '.'.join(opt.split('.')[1:]).strip()
				if n != '':
					e[n] = True
		return sorted(e.keys())

	def listPlugins(self, profile):
		return [p.strip() for p in self.get(profile, 'plugins').split(',')]

def new(cfgfile = None):
	log.debug('cfg.new')
	config = Config(
		defaults = _DEFAULT,
		strict = True,
		default_section = 'default',
		empty_lines_in_values = False,
		comment_prefixes = ('#', ),
		delimiters = ('=', ),
	)
	config._init(cfgfile = cfgfile)
	return config
