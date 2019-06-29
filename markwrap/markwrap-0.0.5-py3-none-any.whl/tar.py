'''
Python wrapper for the tar command

Depends on tarfile functionality, but also:
* scopes the valid input
* logs beginning and ending
* liberally raises exceptions
'''

import logging
import os
import tarfile
from . import check

def compress(tarballName, dirs):
	check.absolutePath(tarballName)
	check.nonexistent(tarballName)

	for dir in dirs:
		check.absolutePath(dir)
		check.exists(dir)
		check.isDir(dir)

	if str(tarballName)[-7:] != ".tar.gz":
		logging.error("tarballName must end in .tar.gz: %s", tarballName)
		raise RuntimeError()

	logging.info("Compressing %s into %s", dirs, tarballName)
	with tarfile.open(tarballName, "w:gz") as tar:
		for dir in dirs:
			tar.add(dir, arcname=os.path.basename(dir))
	logging.info("Compressed %s into %s", dirs, tarballName)

def decompress(tarball, destinationPath):
	check.absolutePath(tarball)
	check.absolutePath(destinationPath)

	check.exists(tarball)
	check.isFile(tarball)
	check.nonexistent(destinationPath)

	if not tarfile.is_tarfile(tarball):
		logging.error("tarballName must be a tar file: %s", tarball)
		raise RuntimeError()

	logging.info("Decompressing %s into %s", tarball, destinationPath)
	with tarfile.open(tarball, "r:gz") as tar:
		tar.extractall(destinationPath)
	logging.info("Decompressed %s into %s", tarball, destinationPath)
