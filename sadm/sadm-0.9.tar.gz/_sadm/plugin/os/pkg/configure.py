# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['configure']

def configure(env, cfg):
	env.settings.merge(cfg, 'os.pkg', ('update', 'install', 'remove', 'prune'))
