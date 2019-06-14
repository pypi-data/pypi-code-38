# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

def configure(env, cfg):
	if 'testing' in cfg:
		for opt in cfg['testing']:
			env.settings['testing'][opt] = cfg['testing'][opt]
