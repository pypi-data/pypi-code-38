# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque

__all__ = ['configure']

def configure(env, cfg):
	data = deque()
	for opt in cfg['sync']:
		data.append(getInfo(cfg, opt))
	env.session.set('sync', tuple(data))

def getInfo(cfg, opt):
	i = cfg.getlist('sync', opt)
	inf = {'cfg.opt': opt, 'src': i[0], 'dst': i[1], 'args': dict()}
	if len(i) > 2:
		for arg in i[2:]:
			if arg.startswith('user:'):
				val = arg.split(':')[1]
				inf['args']['user'] = val
			elif arg.startswith('group:'):
				val = arg.split(':')[1]
				inf['args']['gruop'] = val
			elif arg.startswith('filemode:'):
				val = arg.split(':')[1]
				inf['args']['filemode'] = val
			elif arg.startswith('dirmode:'):
				val = arg.split(':')[1]
				inf['args']['dirmode'] = val
	return inf
