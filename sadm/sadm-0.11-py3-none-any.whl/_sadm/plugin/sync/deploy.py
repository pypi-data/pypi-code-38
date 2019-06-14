# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import tarfile
from os import stat

__all__ = ['deploy']

def deploy(env):
	fn = env.name() + '.tar'
	fpath = env.assets.rootdir(env.name(), fn)
	mtime = stat(fpath).st_mtime
	target = env.settings.get('sadmenv', 'target.dir')
	env.log("%s %s" % (fn, mtime))
	env.log("target %s" % target)
	with open(fpath, 'rb') as fh:
		tar = tarfile.open(fn, 'r:', fileobj = fh)
		for tinfo in tar:
			tinfo.mtime = mtime
			env.log("  %s" % tinfo.name)
			tar.extract(tinfo, path = target, set_attrs = True)
		tar.close()
