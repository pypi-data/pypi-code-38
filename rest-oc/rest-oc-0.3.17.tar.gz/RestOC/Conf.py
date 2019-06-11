# coding=utf8
""" Conf Module

Used to set and get conf (json) files
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

# Python imports
import json

# Framework imports
from . import DictHelper

# Confs available
_dmConfs = {}

def get(key = None, default = None, conf = '_'):
	"""Get

	Gets a single value from a conf, returns default if not found

	Arguments:
		key {string|tuple} -- A tuple to find a child key, or a string to find a
			parent key
		default {mixed} -- What to return if the key isn't found
		conf {string} -- The conf to fetch from

	Returns:
		mixed
	"""

	# Import the confs
	global _dmConfs

	# If the conf doesn't exist, return the default
	if conf not in _dmConfs:
		return default

	# If the key is none, return the entire conf
	if key is None:
		return _dmConfs[conf]

	# If the key is a string
	if isinstance(key, str):

		# If the key doesn't exist in the conf, return the default
		if key not in _dmConfs[conf]:
			return default

		# Return the key from the conf
		return _dmConfs[conf][key]

	# If the key is a tuple
	if isinstance(key, tuple):

		# Get the first level
		mRet = _dmConfs[conf]

		# Loop through and find the value
		for i in range(0, len(key)):

			# If we don't have a dict, return the default
			if not isinstance(mRet, dict):
				return default

			# If the key doesn't exist at this level, return the default
			if key[i] not in mRet:
				return default

			# Go deeper
			mRet = mRet[key[i]]

		# Return the value
		return mRet

	# Else, we got something bad
	raise ValueError('%s is not a valid value for key argument of %s' % (str(key), sys._getframe().f_code.co_name))

def load(file, conf = '_'):
	"""Load

	Loads a conf into the specified conf, or 'default', if not set

	Argurments:
		file {str} -- A file to be loaded into the conf
		conf {string} -- The conf to store in

	Returns:
		None
	"""

	# Import the confs
	global _dmConfs

	# Open the file and store the contents
	with open(file) as oF:
		_dmConfs[conf] = json.load(oF)

def load_merge(file, conf = '_'):
	"""Load Merge

	Loads a conf and merges it into whatever already exists

	Args:
		file {str} -- A file to be loaded
		conf {string} -- The conf to update

	Returns:
		None
	"""

	# Import the confs
	global _dmConfs

	# Open the file
	with open(file) as oF:

		# If we have no conf yet, just store it
		if conf not in _dmConfs:
			_dmConfs[conf] = json.load(oF)

		# Else, combine the data
		else:
			_dmConfs[conf] = DictHelper.combine(_dmConfs[conf], json.load(oF))

def set(key, val, conf = '_'):
	"""Set

	Sets a key in the given conf, returns the previous value

	Arguments:
		key {string|tuple} -- A tuple to set a child key, or a string to set a
			parent key
		val {mixed} -- The value to set for the key
		conf {str} -- The conf to set the key for

	Returns:
		mixed
	"""

	# Import the confs
	global _dmConfs

	# If the conf doesn't exist, create it
	if conf not in _dmConfs:
		_dmConfs[conf]

	# If the key is none, set the entire conf
	if key is None:
		_dmConfs[conf] = val
		return None

	# If the key is a string, set it
	if isinstance(key, str):
		mRet = (key in _dmConfs[conf] and _dmConfs[conf][key] or None)
		_dmConfs[conf][key] = val
		return mRet

	# If we got a tuple
	if isinstance(key, tuple):

		# Set the first level
		mSet = _dmConfs[conf]

		# Get the length of keys
		iLen = len(key)

		# Go through each level
		for i in range(0, iLen):

			# If we are on the last level
			if i+1 == iLen:
				mRet = mSet[key[i]]
				mSet[key[i]] = val
				return mRet

			# Else, we are still going deeper
			else:

				# If the level doesn't exist
				if key[i] not in mSet:
					mSet[key[i]] = {}

				# Set the level
				mSet = mSet[key[i]]

	# Else, we got something bad
	raise ValueError('%s is not a valid value for key argument of %s' % (str(key), sys._getframe().f_code.co_name))
