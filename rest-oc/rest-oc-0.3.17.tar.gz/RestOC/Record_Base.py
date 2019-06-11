# coding=utf8
""" Record Base Module

The base concept for all records stored in any sort of DB
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

# Python imports
import abc
import json
from hashlib import md5

# Framework imports
from . import DictHelper

# The global DB prefix
__msPrepend = ''

# The list of registered DB types
__mlTypes = {}

def dbPrepend(pre = None):
	"""DB Prepend

	Gets or sets the global prefix for all DBs, useful for testing/development

	Arguments:
		pre {str} -- The prefix to store

	Returns:
		str|None
	"""

	# If a prefix was passed
	if pre:
		global __msPrepend
		__msPrepend = pre

	# Else return what we have
	else:
		return __msPrepend

def getType(type_):
	"""Get Type

	Returns the module used to work with the specific type

	Arguments:
		type_ {str} -- The name of the type of DB

	Returns:
		module
	"""
	return __mlTypes[type_]

def registerType(type_, module_):
	"""Register Type

	Sets the class instance used for a specific DB type

	Arguments:
		type_ {str} -- The name used for the type of DB
		module_ {module} -- The module being registered

	Throws:
		ValueError

	Returns:
		None
	"""

	# Go through each type and check for an addHost function
	try: getattr(module_, 'addHost')
	except AttributeError: raise ValueError("%s does not have a valid addHost function" % type_)
	try: getattr(module_, 'dbCreate')
	except AttributeError: raise ValueError("%s does not have a valid dbCreate function" % type_)
	try: getattr(module_, 'dbDrop')
	except AttributeError: raise ValueError("%s does not have a valid dbDrop function" % type_)

	# If we got no exceptions, store the module
	global __mlTypes
	__mlTypes[type_] = module_

class RevisionException(Exception):
	"""Revision Exception

	Raised if a record can not be updated do to Revision failure

	Extends:
		Exception
	"""
	pass

class Record(abc.ABC):
	"""Record

	The base class for all child record classes

	Extends:
		abc.ABC
	"""

	def __init__(self, record={}, custom={}):
		"""Constructor

		Initialises the instance and returns it

		Arguments:
			record {dict} -- The record data
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record
		"""

		# Fetch the record structure
		self._dStruct = self.struct(custom)

		# If we received data
		if record:

			# Validate it
			if not self._dStruct['tree'].valid(record, False):
				raise ValueError(self._dStruct['tree'].validation_failures)

		# Store the data and reset the changed flags
		self._dRecord = self._dStruct['tree'].clean(record)
		self._dChanged = {}

		# If we need to keep changes
		if self._dStruct['changes']:
			self._dOldRecord = None

	def __contains__(self, field):
		"""__contains__

		Python magic method for checking a key exists in a dict like object

		Arguments:
			field {str} -- The field to check for

		Returns:
			bool
		"""
		return field in self._dRecord

	def __delitem__(self, field):
		"""__delitem__

		Python magic method for deleting a key from a dict like object

		Arguments:
			field {str} -- The field to delete

		Returns:
			None
		"""
		self.d(field);

	def __getitem__(self, field):
		"""__getitem__

		Python magic method for getting a key from a dict like object

		Arguments:
			field {str} -- The field to return

		Raises:
			KeyError

		Returns:
			mixed
		"""
		return self._dRecord[field]

	def __setitem__(self, field, val):
		"""__setitem__

		Python magic method for setting a key in a dict like object

		Arguments:
			field {str} -- The field to set
			val {mixed} -- The value of the field

		Returns:
			None
		"""
		self.fieldSet(field, val)

	def __str__(self):
		"""__str__

		Python magic method to return a string for the instance

		Returns:
			str
		"""
		return str(self._dRecord)

	def _revision(self, struct, init=False):
		"""Revision

		Internal method for setting revision values

		Arguments:
			struct {dict} -- The structure for the record
			init {bool} -- True to set a new value

		Returns:
			bool
		"""

		# If we are generating a new value
		if init:

			# Remove the _rev value so we don't include it in the MD5
			if struct['rev_field'] in self._dRecord:
				del self._dRecord[struct['rev_field']]

			# Generate and set the revision
			self._dRecord[struct['rev_field']] = '1-%s' % md5(json.dumps(self._dRecord)).hexdigest()

			# Return OK
			return True

		# Else if we are updating the existing revision
		else:

			# Remove and store the existing revision
			sRev = self._dRecord[struct['rev_field']]
			del self._dRecord[struct['rev_field']]

			# Split it into version and hash
			sVer, sHash = sRev.split('-')

			# Generate a new hash from the record data
			sMD5 = md5(json.dumps(self._dRecord)).hexdigest()

			# If the old and new hash don't match
			if sMD5 != sHash:

				# Update the revision
				self._dRecord[info['rev_field']] = '%d-%s' % (int(sVer)+1, sMD5)

				# Flag the revision field as changed
				if self._dChanged != True:
					self._dChanged[info['rev_field']] = True

				# Return OK
				return True

			# The record hasn't actually changed
			return False

	@abc.abstractclassmethod
	def append(cls, _id, array, item, custom={}):
		"""Append

		Adds an item to a given array/list for a specific record

		Arguments:
			_id {mixed} -- The ID of the record to append to
			array {str} -- The name of the field with the array
			item {mixed} -- The value to append to the array
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "append" method')

	def changes(self):
		"""Changes

		Returns the list of changed fields

		Returns:
			list
		"""
		return self._dChanged.keys()

	@abc.abstractclassmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""
		raise NotImplementedError('Must implement the "config" method')

	@abc.abstractclassmethod
	def contains(cls, _id, array, item, custom={}):
		"""Contains

		Checks if a specific item exist inside a given array/list

		Arguments:
			_id {mixed} -- The ID of the record to check
			array {str} -- The name of the field with the array
			item {mixed} -- The value to check for in the array
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "contains" method')

	@abc.abstractclassmethod
	def count(cls, _id, index=None, filter=None, custom={}):
		"""Count

		Returns the number of records associated with index or filter

		Arguments:
			_ids {mixed} -- The ID to check
			index {str} -- Used as the index instead of the primary key
			filter {dict} -- Additional filter
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "count" method')

	@abc.abstractmethod
	def create(self, conflict='error', changes=None):
		"""Create

		Adds the record to the DB and returns the primary key

		Arguments:
			conflict {str} -- Must be one of 'error', 'replace', or 'update'
			changes {dict} -- Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			mixed|None
		"""
		raise NotImplementedError('Must implement the "create" method')

	@abc.abstractmethod
	def delete(self, changes=None):
		"""Delete

		Deletes the record represented by the instance

		Arguments:
			changes {dict} -- Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "delete" method')

	@abc.abstractclassmethod
	def deleteGet(cls, _id, index=None, custom={}):
		"""Delete Get

		Deletes one or many records by ID or index and returns how many were
		found/deleted

		Arguments:
			_id {mixed|mixed[]} -- The ID(s) to delete or None for all records
			index {str} -- Used as the index instead of the primary key
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Return:
			int
		"""
		raise NotImplementedError('Must implement the "deleteGet" method')

	@abc.abstractclassmethod
	def exists(cls, _id, index=None, custom={}):
		"""Exists

		Returns true if the specified ID or unique index value exists

		Arguments:
			_id {mixed} -- The ID to check
			index {str} -- Used as the index instead of the primary key
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "exists" method')

	def fieldDelete(self, field):
		"""Field Delete

		Deletes a specific field from a record (used by __delitem__)

		Arguments:
			field {str} -- The field to delete

		Raises:
			KeyError

		Returns:
			self
		"""

		# Raise a key error if the field doesn't exist in the record
		if field not in self._dRecord:
			raise KeyError(field)

		# Remove the field from the document
		del self._dRecord[field]

		# Flag the entire document as needing to be updated
		self._dChanged = True

		# Return ok
		return self

	def fieldGet(self, field, default=None):
		"""Field Get

		Returns a specific field, if it's not found, returns the default

		Arguments:
			field {str} -- The field to get
			default {mixed} -- Returned if the field doesn't exist

		Returns:
			mixed
		"""

		# If the field doesn't exist
		if field not in self._dRecord:
			return default

		# Return the field
		return self._dRecord[field]

	def fieldSet(self, field, val):
		"""Field Set

		Sets a specific field in a record (used by __setitem__)

		Arguments:
			field {str} -- The name of the field to set
			val {mixed} -- The value to set the field to

		Returns:
			self for chaining

		Raises:
			KeyError: field doesn't exist in the structure of the record
			ValueError: value is not valid for the field
		"""

		# Get the structure associated with the record
		dStruct = self.struct()

		# If the field is not valid for the record
		if field not in dStruct['tree']:
			raise KeyError(field)

		# If the value isn't valid for the field
		if not dStruct['tree'][field].valid(val, [field]):
			raise ValueError(dStruct['tree'][field].validation_failures)

		# If we need to keep changes
		if self._dStruct['changes']:
			if self._dOldRecord is None:
				self._dOldRecord = DictHelper.clone(self._dRecord)

		# If the value is not None, store it after cleaning it
		if val is not None:
			self._dRecord[field] = dStruct['tree'][field].clean(val)
		else:
			self._dRecord[field] = None

		# If we still have a dict for changes (not a total replace)
		if isinstance(self._dChanged, dict):
			self._dChanged[field] = True

		# Allow chaining
		return self

	@abc.abstractclassmethod
	def filter(cls, fields, raw=None, orderby=None, custom={}):
		"""Filter

		Finds records based on the specific fields and values passed

		Arguments:
			fields {dict} -- A dictionary of field names to the values they
				should match
			raw {bool|list} -- Return raw data (dict) for all or a set list of
				fields
			orderby {str|str[]} -- A field or fields to order the results by
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record[]|dict[]
		"""
		raise NotImplementedError('Must implement the "filter" method')

	@classmethod
	def generateChanges(cls, old, new):
		"""Generate Changes

		Generates the list of changes between two records

		Arguments:
			old {dict} -- Old record
			new {dict} -- New record

		Returns:
			dict|None
		"""

		# If we are dealing with a dict
		if isinstance(old, dict):

			# If the new is not also a dict
			if not isinstance(new, dict):
				return {"old":old, "new":new}

			# Both are dicts, create a new dict to return
			dRet = {}

			# Get the length of keys in old
			iOldLen = len(old.keys())

			# Store the keys from new and get the length
			lNewKeys = list(new.keys())
			iNewLen = len(lNewKeys)

			# Start checking keys from old
			for k in old:

				# If the key doesn't exist in new
				if k not in new:
					dRet[k] = {"old":old[k], "new":None}
					continue

				# It exists in both so pass the two along and remove the key
				#	from the new list
				dTemp = cls.generateChanges(old[k], new[k])
				lNewKeys.remove(k)

				# If there's a value, store it
				if dTemp: dRet[k] = dTemp

			# If there's any keys left in the new list
			if lNewKeys:
				for k in lNewKeys:
					dRet[k] = {"old":None, "new": new[k]}

			# If the number of keys different match all data, set everything as
			#	changed
			iMaxKeys = iOldLen > iNewLen and iOldLen or iNewLen
			if len(dRet.keys()) >= iMaxKeys:
				return {"old":old, "new":new}

			# Return the changes if there are any
			if dRet: return dRet

		# Else if we are dealing with a list
		elif isinstance(old, list):

			# If the new is not also a list
			if not isinstance(new, list):
				return {"old":old, "new":new}

			# Both are lists, create a new dict to return
			dRet = {}

			# Get the length of the old and new
			iOldLen = len(old)
			iNewLen = len(new)

			# Start going through the indexes of the old
			for i in range(iOldLen):

				# If it's not in the new
				if i >= iNewLen:
					dRet[str(i)] = {"old":old[i], "new":None}
					continue

				# It exists in both so pass the two along
				dTemp = cls.generateChanges(old[i], new[i])

				# If there's a value, store it
				if dTemp: dRet[str(i)] = dTemp

			# If there's more new indexes than old
			if iNewLen > iOldLen:
				for i in range(iOldLen, iNewLen):
					dRet[str(i)] = {"old":None, "new":new[i]}

			# If the number of indexes different match all data, set everything
			#	as changed
			iMaxKeys = iOldLen > iNewLen and iOldLen or iNewLen
			if len(dRet.keys()) >= iMaxKeys:
				return {"old":old, "new":new}

			# Return the changes if there are any
			if dRet: return dRet

		# Else it's a single value
		else:

			# If the new is a dict or list or the values don't match
			if isinstance(new, (dict,list)) or new != old:
				return {"old":old, "new":new}

		# No changes
		return None

	@staticmethod
	def generateConfig(tree, special='db', db=None):
		"""Generate Config

		Generates record specific config based on the Format-OC tree passed

		Arguments:
			tree {FormatOC.Tree} -- the tree associated with the record type
			special {str} -- The special section used to identify the child info

		Returns:
			dict
		"""

		# Combine the dicts
		dRet = DictHelper.combine({
			"auto_primary": True,
			"changes": False,
			"db": 'test',
			"indexes": {},
			"table": "table",
			"primary": "_id",
			"rev_field": '_rev',
			"revisions": False,
			"tree": tree
		}, tree.special(special, default={}))

		# If there's a specific DB
		if db:
			dRet['db'] = db

		# Return the values
		return dRet

	@abc.abstractclassmethod
	def get(cls, _id=None, index=None, filter=None, match=None, raw=None, orderby=None, limit=None, custom={}):
		"""Get

		Returns records by ID or index, can also be given an extra filter

		Arguments:
			_id {mixed|mixed[]} -- The ID(s) to fetch from the table
			index {str} -- Index to use instead of primary key
			filter {dict} -- Additional filter
			match {tuple} -- Name/Match filter
			raw {bool|list} -- Return raw data (dict) for all or a set list of
				fields
			orderby {str|str[]} -- A field or fields to order the results by
			limit {int|tuple} -- The limit and possible starting point
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record|Record[]|dict|dict[]
		"""
		raise NotImplementedError('Must implement the "get" method')

	@abc.abstractclassmethod
	def getChanges(cls, _id, orderby=None, custom={}):
		"""Get Changes

		Returns the changes record associated with the primary record and table.
		Used by Record types that have the 'changes' flag set

		Arguments:
			_id {mixed} -- The of the primary record to fetch changes for
			orderby {str|str[]} -- A field or fields to order the results by
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			dict
		"""
		raise NotImplementedError('Must implement the "get" method')

	@classmethod
	def struct(cls, custom={}):
		"""Struct

		Returns structure info for the record based on the DB and Tree

		Arguments:
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			dict
		"""

		# Get the config values associated with the Child record
		dConfig = DictHelper.clone(cls.config())

		# If the host value is overriden
		if 'host' in custom:
			dConfig['host'] = custom['host']

		# Add the global prefix
		dConfig['db'] = dbPrepend() + dConfig['db']

		# If we received an append value
		if 'append' in custom:
			dConfig['db'] = "%s_%s" % (dConfig['db'], custom['append'])

		# Return the structure
		return dConfig

	def record(self):
		"""Record

		Returns the record data as a dict

		Returns:
			dict
		"""
		return DictHelper.clone(self._dRecord)

	@abc.abstractclassmethod
	def remove(cls, _id, array, index, custom={}):
		"""Remove

		Removes an item from a given array/list for a specific record

		Arguments:
			_id {mixed} -- The ID of the record to remove from
			array {str} -- The name of the field with the array
			index {uint} -- The index of the array to remove
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "remove" method')

	@abc.abstractmethod
	def save(self, replace=False, changes=None):
		"""Save

		Updates the record in the DB and returns true if anything has changed,
		or a new revision number of the record is revisionable

		Arguments:
			replace {bool} -- If true, replace all fields instead of updating
			changes {dict} -- Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool|str
		"""
		raise NotImplementedError('Must implement the "update" method')

	@classmethod
	@abc.abstractmethod
	def tableCreate(cls, custom={}):
		"""Table Create

		Creates the record's table/collection/etc in the DB

		Arguments:
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "tableCreate" method')

	# tableDelete static method
	@classmethod
	@abc.abstractmethod
	def tableDrop(cls, custom={}):
		"""Table Drop

		Deletes the record's table/collection/etc in the DB

		Arguments:
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "tableDrop" method')

	@classmethod
	def tableName(cls):
		"""Table Name

		Returns the name for the given record child class

		Returns:
			str
		"""
		return cls.struct()['table']

	@abc.abstractclassmethod
	def updateField(cls, field, value, _id=None, index=None, filter=None):
		"""Updated Field

		Updates a specific field to the value for an ID, many IDs, or the entire
		table. Returns the number of records altered

		Arguments:
			field {str} -- The name of the field to update
			value {mixed} -- The value to set the field to
			_id {mixed} -- Optional ID(s) to filter by
			index {str} -- Optional name of the index to use instead of primary
			filter {dict} -- Optional filter list to decide what records get updated

		Returns:
			uint
		"""
		raise NotImplementedError('Must implement the "updateField" method')

	@abc.abstractclassmethod
	def uuid(custom={}):
		"""UUID

		Returns a universal unique ID

		Arguments:
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			str
		"""
		raise NotImplementedError('Must implement the "uuid" method')
