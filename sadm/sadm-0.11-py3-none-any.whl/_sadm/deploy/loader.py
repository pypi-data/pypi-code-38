# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys
from os import path, makedirs, unlink, chmod
from shutil import rmtree, unpack_archive
from subprocess import call

from _sadm import log, cfg, deploy

def loadenv(filename): # pragma: no cover
	envfn = path.realpath(filename)
	log.msg("%s: load" % envfn)
	rc = _check(envfn)
	if rc != 0:
		return rc
	if path.isfile(envfn + '.asc'):
		rc = _verify(envfn)
		if rc != 0:
			return rc
	rc = call("sha256sum -c %s" % envfn, shell = True)
	if rc != 0:
		log.error('env checksum failed!')
		return rc
	_importenv(envfn)
	return 0

def _check(envfn):
	env = path.basename(envfn)[:-4]
	config = cfg.new(deploy.cfgfile)
	if not env in config.listEnvs('deploy'):
		log.error("%s env not found" % env)
		return 1
	return 0

def _verify(envfn):
	rc = call("gpg --no-tty --no --verify %s.asc %s 2>/dev/null" % (envfn, envfn),
		shell = True)
	if rc == 0:
		log.msg("%s: OK" % envfn)
	else:
		log.error('env signature verify failed!')
	return rc

def _importenv(envfn):
	srcfn = envfn[:-4]
	rootdir = path.dirname(path.dirname(envfn))
	deploydir = path.join(rootdir, 'deploy')
	envdir = path.join(deploydir, path.basename(srcfn))
	if path.isdir(envdir): # pragma: no cover
		rmtree(envdir)
	makedirs(envdir)
	chmod(envdir, 0o0700)
	log.msg("%s.zip: unpack" % srcfn)
	unpack_archive(srcfn + '.zip', extract_dir = envdir, format = 'zip')
