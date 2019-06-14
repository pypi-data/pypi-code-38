# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, unlink, makedirs
from shutil import rmtree, copytree, copyfile

__all__ = ['lock', 'unlock', 'fpath', 'create', 'sync', 'copy']

def lock(env):
	bdir = env.build.rootdir()
	env.log("build dir %s" % bdir)
	fn = path.normpath(bdir) + '.lock'
	env.debug("lock %s" % fn)
	env.session.set('lockfn', fn)
	makedirs(path.dirname(bdir), exist_ok = True)
	try:
		fh = open(fn, 'x')
	except FileExistsError:
		raise env.error("lock file exists: %s" % fn)
	fh.write('1')
	fh.flush()
	fh.close()
	_cleandir(env, bdir)

def unlock(env):
	fn = env.session.get('lockfn')
	env.debug("unlock %s" % fn)
	try:
		unlink(fn)
	except FileNotFoundError:
		raise env.error("unlock file not found: %s" % fn)

def _cleandir(env, bdir):
	base = path.normpath(bdir)
	bdirs = [
		bdir,
		base + '.meta',
	]
	bfiles = [
		base + '.zip',
		base + '.env',
		base + '.env.asc',
		base + '.deploy',
	]
	for d in bdirs:
		if path.isdir(d):
			env.debug("rmtree %s" % d)
			rmtree(d) # clean tree
		env.debug("makedirs %s" % d)
		makedirs(d) # recreate base dirs
	for f in bfiles:
		if path.isfile(f):
			env.debug("unlink %s" % f)
			unlink(f)

def _open(env, filename, mode = 'r', meta = False):
	fn = fpath(env, filename, meta = meta)
	if mode != 'r':
		dstdir = path.dirname(fn)
		if not path.isdir(dstdir):
			env.debug("makedirs %s" % dstdir)
			makedirs(dstdir, exist_ok = True)
	env.debug("open(%s) %s" % (mode, fn))
	return open(fn, mode)

def fpath(env, *parts, meta = False):
	bdir = env.build.rootdir()
	if meta:
		bdir = path.normpath(bdir) + '.meta'
	fn = path.join(*parts)
	fn = path.normpath(fn)
	if fn.startswith(path.sep):
		fn = fn.replace(path.sep, '', 1)
	return path.realpath(path.join(bdir, fn))

def create(env, filename, meta = False, **kwargs):
	fh = _open(env, filename, mode = 'x', meta = meta)
	if not meta:
		env.build.addfile(filename, **kwargs)
	return fh

def sync(env, src, dst, **kwargs):
	srcdir = env.assets.rootdir(src)
	dstdir = fpath(env, dst)
	copytree(srcdir, dstdir, symlinks = False)
	env.build.adddir(dst, **kwargs)

def copy(env, src, dst, **kwargs):
	srcfn = env.assets.rootdir(src)
	dstfn = fpath(env, dst)
	dstdir = path.dirname(dstfn)
	if not path.isdir(dstdir):
		makedirs(dstdir)
	copyfile(srcfn, dstfn, follow_symlinks = False)
	env.build.addfile(dst, **kwargs)
