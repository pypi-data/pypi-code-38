'''
Common input validation checks

Every input must be an absolute path
'''
import logging
import os

def nonNone(obj):
	if obj == None:
		logging.error("can NOT be None: %s", obj)
		raise RuntimeError()

def absolutePath(path):
	nonNone(path)
	if not os.path.isabs(path):
		logging.error("path must be an absolute path: %s", path)
		raise RuntimeError()

def exists(path):
	absolutePath(path)

	if not os.path.exists(path):
		logging.error("file or directory does not exist: %s", path)
		raise RuntimeError()

def nonexistent(path):
	absolutePath(path)

	if os.path.exists(path):
		logging.error("file or directory already exists: %s", path)
		raise RuntimeError()

def isFile(f):
	exists(f)

	if not os.path.isfile(f):
		logging.error("f is not a file: %s", f)
		raise RuntimeError()

def isDir(d):
	exists(d)

	if not os.path.isdir(d):
		logging.error("d is not a directory: %s", d)
		raise RuntimeError()
