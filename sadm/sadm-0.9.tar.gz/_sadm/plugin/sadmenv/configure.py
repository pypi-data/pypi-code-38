# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import shutil

__all__ = ['configure']

def configure(env, cfg):
	env.debug("archive formats: %s" % [a[0] for a in shutil.get_archive_formats()])
	env.settings.merge(cfg, 'sadmenv', ('target.dir',))
