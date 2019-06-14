# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from time import strftime, time

from _sadm.errors import PluginError

__all__ = ['run']

_validAction = {
	'build': True,
	'deploy': True,
}

def run(env, action):
	_start = time()
	env.info("%s start %s" % (action, strftime('%c %z')))
	env.log("%s %s" % (env.config.name(), env.config.filename()))
	try:
		if not _validAction.get(action, False):
			raise env.error("invalid action %s" % action)
		with env.lock() as env:
			env.configure()
			_runPreAction(env, action)
			_runAction(env, action)
			_runPostAction(env, action)
			env.report(action, startTime = _start)
	finally:
		env.info("%s end %s" % (action, strftime('%c %z')))

def _runAction(env, action, cmd = None, force = False, revert = False):
	if cmd is None:
		cmd = action
	for p in env.settings.plugins(action, revert = revert):
		if hasattr(p.mod, cmd):
			func = getattr(p.mod, cmd)
			tag = "%s.%s" % (cmd, p.name)
			env.start(tag)
			func(env)
			env.end(tag)
		else:
			env.debug("%s plugin no action %s" % (p.name, cmd))
			if force:
				raise PluginError("%s plugin no action %s" % (p.name, cmd))

def _runPreAction(env, action):
	_runAction(env, action, cmd = "pre_%s" % action)

def _runPostAction(env, action):
	_runAction(env, action, cmd = "post_%s" % action, revert = True)
