# -*- coding: utf-8 -*-
"""
Utilities for computing checksum of file
"""

import hashlib
from base64 import b64encode


def checksum(file_path, hash_object):
	""" Caculate checksum of file at `file_path` with `hash_object`.

	Bytes from file at given path will feed into the hash object.
	The same hash object will return one completed.

	Args:
		file_path - Path of file to compute checksum.
		hash_object - Hash object for computing the checksum.

	Return:
		The same `hash_object` in parameter.
	"""
	# buffer size (128 KiB) came from:
	# https://github.com/coreutils/coreutils/blob/master/src/ioblksize.h#L23
	buf = bytearray(131072)
	mmv = memoryview(buf)
	with open(file_path, "rb", buffering=0) as fp:
		n = fp.readinto(mmv)
		while n:
			hash_object.update(mmv[:n])
			n = fp.readinto(mmv)
	return hash_object


def b64digest(hash_object):
	""" Encode digest result into Base64 with `=` stripped.

	This function only supports fixed length digest (the `digest()` method
	does not require `length` parameter).

	Args:
		hash_object - Hash object contains digest result.

	Return:
		Base64 encoded digest string with padding stripped.
	"""
	return b64encode(hash_object.digest()).rstrip(b'=').decode('ascii')


def md5sum(file_path):
	""" Caculate MD5 checksum of gievn file.

	Args:
		file_path - The path of file to caculate MD5 checksum.

	Return:
		A hash object contains digest of bytes from given file.
	"""
	return checksum(file_path, hashlib.md5())


def sha256sum(file_path):
	""" Caculate SHA-256 checksum of gievn file.

	Args:
		file_path - The path of file to caculate SHA-256 checksum.

	Return:
		A hash object contains digest of bytes from given file.
	"""
	return checksum(file_path, hashlib.sha256())


def sha512sum(file_path):
	""" Caculate SHA-512 checksum of gievn file.

	Args:
		file_path - The path of file to caculate SHA-512 checksum.

	Return:
		A hash object contains digest of bytes from given file.
	"""
	return checksum(file_path, hashlib.sha512())
