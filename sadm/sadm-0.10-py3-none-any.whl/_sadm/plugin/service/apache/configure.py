# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['configure']

def configure(env, cfg):
	env.settings.merge(cfg, 'service.apache', (
		'conf.disable',
		'mod.disable',
		'site.disable',
		'conf.enable',
		'mod.enable',
		'site.enable',
	))
