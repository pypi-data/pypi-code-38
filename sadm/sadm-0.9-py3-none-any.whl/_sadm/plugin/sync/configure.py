# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque

__all__ = ['configure']

def configure(env, cfg):
	data = deque()
	for opt in cfg['sync']:
		i = cfg.getlist('sync', opt)
		data.append({'src': i[0], 'dst': i[1]})
	env.session.set('sync', tuple(data))
