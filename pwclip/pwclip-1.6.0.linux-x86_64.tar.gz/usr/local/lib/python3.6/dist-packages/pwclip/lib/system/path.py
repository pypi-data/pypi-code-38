"""path related functions"""
from re import search
from os import getcwd, chdir, chmod, walk, \
    readlink, utime, stat as osstat
from os.path import expanduser, islink, \
    isfile, isdir, abspath, join as pjoin, exists
from time import time
from shutil import copy2
from configparser import ConfigParser as _ConfPars
from json import load as _jsonload

from system.random import randin

def absrelpath(path, base=None):
	"""absrelpath for finding absolute paths in optional given base"""
	base = base if base else getcwd()
	path = path.strip("'")
	path = path.strip('"')
	if path.startswith('~'):
		path = expanduser(path)
	if islink(path):
		path = readlink(path)
	if '..' in path or not path.startswith('/'):
		pwd = getcwd()
		chdir(base)
		path = abspath(path)
		chdir(pwd)
	return path.rstrip('/')

def realpaths(pathlist, base=None):
	"""realpaths using realpath on multiple input files"""
	base = base if base else getcwd()
	paths = []
	for path in pathlist:
		if isinstance(path, (list, tuple)):
			#print('list/tuple')
			for _ in path:
				paths = [absrelpath(p, base) for p in path]
		elif isinstance(path, str):
			if ' ' in path:
				#print('liststring')
				paths = [absrelpath(p.strip(), base) for p in path.strip('[]').split(',')]
				break
			else:
				#print('string', path)
				paths.append(absrelpath(path, base))
	return paths

def confpaths(paths, conf, base=''):
	"""find configs in paths in base if file exists"""
	return list(set([pjoin(expanduser('~'), path[2:], conf) \
        for path in paths if path.startswith('~/') and \
        isfile(pjoin(expanduser('~'), path[2:], conf))] + \
        [pjoin(base, path[2:], conf) for path in \
        paths if path.startswith('./') and \
        isfile(pjoin(base, path[2:], conf))] + \
        [pjoin(base, path, conf) for path in paths if not \
        path.startswith('/') and not path.startswith('.') and \
        isfile(pjoin(base, path, conf))] + \
        [pjoin(path, conf) for path in paths if path.startswith('/') and \
        isfile(pjoin(path, conf))]))

def confdats(*confs):
	"""get ini data from config files"""
	cfg = _ConfPars()
	cfgdats = {}
	for conf in confs:
		cfg.read(conf)
		for section in cfg.sections():
			cfgdats[section] = dict(cfg[section])
	return cfgdats

def jconfdats(*confs):
	"""get json data from config files"""
	__dats = {}
	for conf in confs:
		with open(conf, 'r') as stream:
			for (key, val) in _jsonload(stream).items():
				__dats[key] = val
	return __dats

def unsorted(files):
	"""unsort given files"""
	unsorteds = []
	while len(unsorteds) != len(files):
		f = files[randin(len(files))]
		unsorteds.append(f)
	return unsorteds

def filetime(trg):
	"""local file-timestamp method"""
	return int(osstat(trg).st_mtime), int(osstat(trg).st_atime)

def setfiletime(trg, mtime=None, atime=None):
	"""local file-timestamp set method"""
	mt, at = filetime(trg)
	if mtime and not atime:
		atime = at
	elif atime and not mtime:
		mtime = mt
	utime(trg, (at, mt))

def filerotate(lfile, count=3, force=None):
	"""rotate given file by a maximum of count"""
	mode = osstat(lfile).st_mode
	mt, at = filetime(lfile)
	rtn = False
	for i in reversed(range(0, int(count))):
		old = '%s.%d'%(lfile, i)
		if i == 0:
			old = lfile
		new = '%s.%d'%(lfile, int(i+1))
		try:
			with open(old, 'rb') as ofh:
				oldf = ofh.read()
		except FileNotFoundError:
			oldf = None
		try:
			with open(new, 'rb') as nfh:
				newf = nfh.read()
		except FileNotFoundError:
			newf = None
		if oldf == newf:
			continue
		if oldf:
			mode = osstat(old).st_mode
			mt, at = filetime(old)
		elif newf:
			mode = osstat(new).st_mode
			mt, at = filetime(new)
		copy2(old, new)
		chmod(new, mode)
		setfiletime(new, mt, at)
		rtn = True
	return rtn

def filesiter(folder, random=False, includes=[], excludes=[]):
	"""iterate over files for given folder"""
	for (d, _, fs) in walk(absrelpath(folder)):
		reordered = sorted if not random else unsorted
		fs = reordered(fs)
		for f in reordered(fs):
			if excludes and [i for i in excludes if search(i, f)]:
				continue
			if includes and not [i for i in includes if search(i, f)]:
				continue
			f = pjoin(d, f)
			yield f

def linesiter(target, includes=[], excludes=[]):
	__lns = []
	with open(target, 'r') as pfh:
		__lns = pfh.readlines()
	for l in __lns:
		if excludes and [i for i in excludes if search(i, l)]:
			continue
		if includes and not [i for i in includes if search(i, l)]:
			continue
		yield l

def findupper(path, name=None, dirs=None, files=None, links=None):
	"""find parent directory by given pattern"""
	if not name:
		name = path
		path = getcwd()
	while len(path.split('/')) > 1:
		trg = pjoin(path, name)
		if dirs is None and files is None and links is None and exists(trg):
			return trg
		elif links and islink(trg):
			return trg
		elif files and isfile(trg):
			return trg
		elif dirs and isdir(trg):
			return trg
		return findupper(
            '/'.join(p for p in path.split('/')[:-1]),
            name, dirs, files, links)

def findupperdir(path, name=None):
	"""find parent directory by given pattern"""
	return findupper(path, name, dirs=True)
