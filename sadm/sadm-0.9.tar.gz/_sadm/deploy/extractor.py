# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import json

from base64 import b64encode
from os import path, chmod

from _sadm import version, libdir
from _sadm.errors import BuildError

__all__ = ['gen']

def gen(env):
	_vars = {
		'env': env.name(),
		'rootdir': path.join(path.sep, 'opt', 'sadm'),
	}
	try:
		env.log("%s.deploy" % env.name())
		base = path.normpath(env.build.rootdir())
		fn = base + '.deploy'
		_write(fn, _getcargo(env, base), _vars)
	except FileExistsError:
		raise BuildError("%s file exists" % fn)

def _getcargo(env, base):
	cargo = {}
	for ext in ('.zip', '.env', '.env.asc'):
		name = base + ext
		if path.isfile(name):
			env.log("load %s" % path.basename(name))
			cargo[env.name() + ext] = _load(name)
		else:
			if ext != '.env.asc':
				raise BuildError("%s file not found" % name)
	return cargo

def _load(fn):
	with open(fn, 'rb') as fh:
		return b64encode(fh.read()).decode()

def _write(fn, cargo, _vars):
	sk = True
	indent = '\t'
	with libdir.openfile('deploy', 'self_extract.py') as src:
		with open(fn, 'x', encoding = 'utf-8') as fh:
			for line in src.readlines():
				if line.startswith('_cargo'):
					fh.write("_cargo = %s\n" % json.dumps(cargo,
						indent = indent, sort_keys = sk))
				elif line.startswith('_vars'):
					fh.write("_vars = %s\n" % json.dumps(_vars,
						indent = indent, sort_keys = sk))
				else:
					fh.write(line)
			fh.write("\n# sadm version %s\n" % version.get())
			fh.flush()
	chmod(fn, 0o0500)
