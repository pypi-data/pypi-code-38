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

def compress(tarballName, dirs):
	## Ensure tarballName does not exist
	if os.path.exists(tarballName):
		logging.error("tarballName already exists: %s", tarballName)
		raise RuntimeError()

	## Ensure tarballName is absolute path
	if not os.path.isabs(tarballName):
		logging.error("tarballName must be an absolute path: %s", tarballName)
		raise RuntimeError()

	## Ensure tarballName ends with .tar.gz
	if str(tarballName)[-7:] != ".tar.gz":
		logging.error("tarballName must end in .tar.gz: %s", tarballName)
		raise RuntimeError()

	## Ensure dirs exist, are directories, and are absolute paths
	for dir in dirs:
		if not os.path.exists(dir):
			logging.error("Cannot compress non-existant directory: %s", dir)
			raise RuntimeError()
		if not os.path.isdir(dir):
			logging.error("Cannot compress non-directory: %s", dir)
			raise RuntimeError()
		if not os.path.isabs(dir):
			logging.error("dir must be an absolute path: %s", dir)
			raise RuntimeError()

	logging.info("Compressing %s into %s", dirs, tarballName)
	with tarfile.open(tarballName, "w:gz") as tar:
		for dir in dirs:
			tar.add(dir, arcname=os.path.basename(dir))
	logging.info("Compressed %s into %s", dirs, tarballName)

def decompress(tarballName, destinationPath):
	## Ensure tarballName exists
	if not os.path.exists(tarballName):
		logging.error("tarballName does not exist: %s", tarballName)
		raise RuntimeError()

	## Ensure tarballName is absolute path
	if not os.path.isabs(tarballName):
		logging.error("tarballName must be an absolute path: %s", tarballName)
		raise RuntimeError()

	## Ensure tarballName is tarfile
	if not tarfile.is_tarfile(tarballName):
		logging.error("tarballName must be a tar file: %s", tarballName)
		raise RuntimeError()

	## Ensure destinationPath does not exist
	if os.path.exists(destinationPath):
		logging.error("destinationPath already exists: %s", destinationPath)
		raise RuntimeError()

	## Ensure destinationPath is absolute path
	if not os.path.isabs(destinationPath):
		logging.error("destinationPath must be an absolute path: %s", destinationPath)
		raise RuntimeError()

	logging.info("Decompressing %s into %s", tarballName, destinationPath)
	with tarfile.open(tarballName, "r:gz") as tar:
		tar.extractall(destinationPath)
	logging.info("Decompressed %s into %s", tarballName, destinationPath)
