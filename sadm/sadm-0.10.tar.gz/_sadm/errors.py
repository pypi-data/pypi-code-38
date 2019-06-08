# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

class Error(Exception):
	typ = None
	msg = None

	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return "%s: %s" % (self.typ, self.msg)

	def __repr__(self):
		return "<sadm.%s: %s>" % (self.typ, self.msg)

	def __eq__(self, err):
		return self.typ == err.typ

	def __hash__(self):
		return hash(self.typ)

class ProfileError(Error):
	typ = 'ProfileError'

class EnvError(Error):
	typ = 'EnvError'

class SettingsError(Error):
	typ = 'SettingsError'

class SessionError(Error):
	typ = 'SessionError'

class AssetError(Error):
	typ = 'AssetError'

class AssetNotFoundError(Error):
	typ = 'AssetNotFoundError'

class BuildError(Error):
	typ = 'BuildError'

class PluginError(Error):
	typ = 'PluginError'

class PluginCommandError(Error):
	typ = 'PluginCommandError'

class PluginScriptNotFound(PluginError):
	typ = 'PluginScriptNotFound'

class PluginScriptNoExec(PluginError):
	typ = 'PluginScriptNoExec'

class PluginScriptTimeout(PluginError):
	typ = 'PluginScriptTimeout'
