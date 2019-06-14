# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.plugin.utils import cmd
from _sadm.plugin.utils.scripts import Scripts

__all__ = ['deploy']

scripts = Scripts('service.apache')

def deploy(env):
	_reload = False
	args = env.settings.getlist('service.apache', 'conf.disable')
	if len(args) > 0:
		env.log('conf.disable')
		_reload = True
		scripts.run('disconf.sh', args)
	args = env.settings.getlist('service.apache', 'mod.disable')
	if len(args) > 0:
		env.log('mod.disable')
		_reload = True
		scripts.run('dismod.sh', args)
	args = env.settings.getlist('service.apache', 'site.disable')
	if len(args) > 0:
		env.log('site.disable')
		_reload = True
		scripts.run('dissite.sh', args)
	args = env.settings.getlist('service.apache', 'conf.enable')
	if len(args) > 0:
		env.log('conf.enable')
		_reload = True
		scripts.run('enconf.sh', args)
	args = env.settings.getlist('service.apache', 'mod.enable')
	if len(args) > 0:
		env.log('mod.enable')
		_reload = True
		scripts.run('enmod.sh', args)
	args = env.settings.getlist('service.apache', 'site.enable')
	if len(args) > 0:
		env.log('site.enable')
		_reload = True
		scripts.run('ensite.sh', args)
	if _reload:
		scripts.run('reload.sh')
