# coding=utf8
"""Record ReDB Module

Extends Record module to add support for RethinkDB tables
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

# Python imports
from hashlib import md5
import sys
from time import sleep, time

# Pip imports
from rethinkdb import errors as rerrors, net as rnet, RethinkDB
r = RethinkDB()

# Framework imports
from . import DictHelper, Record_Base

# List of available hosts
__mdHosts = {}

# defines
MAX_RETRIES = 3

def _connect(host, error_count=0):
	"""Connect

	Internal module function to fetch a connection to a specific RethinkDB host

	Arguments:
		host {str} -- The name the host is stored under using addHost()
		error_count {int} -- The number of times the function has failed

	Raises:
		ConnectionError

	Returns:
		rethinkdb.net.DefaultConnection
	"""

	# If no such host has been added
	if host not in __mdHosts:
		raise ValueError('no such host "%s"' % str(host))

	# Try to connect
	try:
		oCon = r.connect(**__mdHosts[host])

	# Check for driver errors
	except rerrors.RqlDriverError as e:

		# If there was an error, increment the error count
		error_count += 1

		# Raise an exception if we've tried enough times
		if error_count == MAX_RETRIES:
			raise ConnectionError(*e.args)

		# Sleep and try again
		else:
			sleep(1)
			return _connect(host, error_count)

	# Return the connection
	return oCon

class _with(object):
	"""_with

	Used with the special Python with method to create a connection that will
	always be closed regardless of exceptions

	Extends:
		object
	"""

	def __init__(self, host):
		self.con = _connect(host)

	def __enter__(self):
		return self.con

	def __exit__(self, exc_type, exc_value, traceback):
		self.con.close()
		if exc_type is not None:
			return False

def addHost(name, info, update=False):
	"""Add Host

	Add a host that can be used by Records

	Arguments:
		name {str} -- The name that will be used to fetch the host credentials
		info {dict} -- The necessary credentials to connect to the host

	Returns:
		bool
	"""

	# If the info isn't already stored, or we want to overwrite it, store it
	if name not in __mdHosts or update:
		__mdHosts[name] = info
		return True

	# Nothing to do, not OK
	return False

def dbCreate(name, host = 'primary'):
	"""DB Create

	Creates a DB on the given host

	Arguments:
		name {str} -- The name of the DB to create
		host {str} -- The name of the host the DB will be on

	Returns:
		bool
	"""

	try:

		# Fetch the connection
		with _with(host) as oCon:

			# Create the DB
			dRes = r.db_create("%s%s" % (Record_Base.dbPrepend(), name)).run(oCon)

			# If for some reason the DB wasn't created
			if 'dbs_created' not in dRes or not dRes['dbs_created']:
				return False

	# If the DB already exists
	except rerrors.ReqlOpFailedError:
		return True

	# Unknown runtime error
	except rerrors.RqlRuntimeError:
		return False

	# Return OK
	return True

def dbDrop(name, host = 'primary'):
	"""DB Drop

	Drops a DB on the given host

	Arguments:
		name {str} -- The name of the DB to delete
		host {str} -- The name of the host the DB is on

	Returns:
		bool
	"""

	try:

		# Fetch the connection
		with _with(host) as oCon:

			# Delete the DB
			dRes = r.db_drop("%s%s" % (Record_Base.dbPrepend(), name)).run(oCon)

			# If for some reason the DB wasn't dropped
			if 'dbs_dropped' not in dRes or not dRes['dbs_dropped']:
				return False

	# If the DB doesn't exist
	except rerrors.RqlRuntimeError:
		return False

	# Return OK
	return True

class Record(Record_Base.Record):
	"""Record

	Extends the base Record class

	Extends:
		Record_Base.Record
	"""

	@classmethod
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

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Append the org
			dRes = r \
				.db(dStruct['db']) \
				.table(dStruct['table']) \
				.get(_id) \
				.update({array: r.row[array].append(item)}) \
				.run(oCon)

			# Return True if a record was changed
			return dRes['replaced'] == 1

		# Return False
		return False

	@classmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""
		raise NotImplementedError('Must implement the "config" method')

	@classmethod
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

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Check if the org exists
			return r \
				.db(dStruct['db']) \
				.table(dStruct['table']) \
				.get(_id)[array] \
				.contains(item) \
				.run(oCon)

	@classmethod
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

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If an index is passed
		if index:

			# If the index doesn't exist
			if index not in dStruct['indexes']:
				raise KeyError('no index named "%s" in the structure' % index)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Create a cursor for all records
			oCur = r \
				.db(dStruct['db']) \
				.table(dStruct['table'])

			# If there's no primary key, we want all records
			if _id == None:
				pass

			# Else, if there's an index
			elif index:

				# If we recieved a dict for the primary key
				if isinstance(_id, dict):

					# Between two points
					if 'between' in _id:
						oCur = oCur.between(_id['between'][0], _id['between'][1], index=index, right_bound='closed')

					# Greater than
					elif 'gt' in _id:
						oCur = oCur.between(_id['gt'], r.maxval, index=index, left_bound='open')

					# Greater than or equal
					elif 'gte' in _id:
						oCur = oCur.between(_id['gte'], r.maxval, index=index)

					# Less than
					elif 'lt' in _id:
						oCur = oCur.between(r.minval, _id['lt'], index=index)

					# Less than or equal
					elif 'lte' in _id:
						oCur = oCur.between(r.minval, _id['lte'], index=index, right_bound='closed')

					# Invalid request
					else:
						raise ValueError('_id', _id)

				# If we received a tuple
				elif isinstance(_id, tuple):

					# Look for None values
					iNone = -1
					for i in range(len(_id)):
						if _id[i] is None:
							if iNone != -1:
								raise ValueError('_id', 'only one None per tuple')
							iNone = i

					# If there us a None in the tuple, assume between and
					#	replace them with the min and max
					if iNone > -1:
						idMax = list(_id)
						idMin = list(_id)
						idMax[iNone] = r.maxval
						idMin[iNone] = r.minval
						oCur = oCur.between(idMin, idMax, index=index)

					# No None, pass as is
					else:
						oCur = oCur.get_all(_id, index=index)

				# If we get a list, it's a complex index
				elif isinstance(_id, list):
					oCur = oCur.get_all(r.args(_id), index=index)

				# Else, pass as is
				else:
					oCur = oCur.get_all(_id, index=index)

			# If we are using the primary key
			else:

				# If we recieved a dict for the primary key
				if isinstance(_id, dict):

					# Between two points
					if 'between' in _id:
						oCur = oCur.between(_id['between'][0], _id['between'][1], right_bound='closed')

					# Greater than
					elif 'gt' in _id:
						oCur = oCur.between(_id['gt'], r.maxval, left_bound='open')

					# Greater than or equal
					elif 'gte' in _id:
						oCur = oCur.between(_id['gte'], r.maxval)

					# Less than
					elif 'lt' in _id:
						oCur = oCur.between(r.minval, _id['lt'])

					# Less than or equal
					elif 'lte' in _id:
						oCur = oCur.between(r.minval, _id['lte'], right_bound='closed')

					# Invalid request
					else:
						raise ValueError('_id', _id)

				# If we received a tuple
				elif isinstance(_id, tuple):

					# Look for None values
					iNone = -1
					for i in range(len(_id)):
						if _id[i] is None:
							if iNone != -1:
								raise ValueError('_id', 'only one None per tuple')
							iNone = i

					# If there us a None in the tuple, assume between and
					#	replace them with the min and max
					if iNone > -1:
						idMax = list(_id)
						idMin = list(_id)
						idMax[iNone] = r.maxval
						idMin[iNone] = r.minval
						oCur = oCur.between(idMin, idMax)

					# No None, pass as is
					else:
						bMulti = False
						oCur = oCur.get(_id)

				# If we got multiple primary keys, use get all
				elif isinstance(_id, list):
					oCur = oCur.get_all(*_id)

				# If we want one record, change the multi flag, and use get
				else:
					bMulti = False
					oCur = oCur.get(_id)

			# If we want to filter the data further
			if filter:

				# If we got a list
				if isinstance(filter, (list,tuple)):
					oCur = oCur.filter(*filter)
				else:
					oCur = oCur.filter(filter)

			# Run the request and return the count
			try:
				return oCur.count().run(oCon)

			# Catch operational errors
			except rerrors.ReqlOpFailedError as e:

				# An invalid index was passed
				if e.args[0][:5] == 'Index':
					raise KeyError('no index named "%s" in the table' % index)

				# Else, re-raise
				raise e

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

		# Make sure conflict arg is valid
		if conflict not in ('error', 'replace', 'update'):
			raise ValueError('conflict', conflict)

		# If the record requires revisions, make the first one
		if self._dStruct['revisions']:
			self._revision(True)

		# Get a connection to the host
		with _with(self._dStruct['host']) as oCon:

			# Create a new record
			dRes = r \
				.db(self._dStruct['db']) \
				.table(self._dStruct['table']) \
				.insert(self._dRecord, conflict=conflict) \
				.run(oCon)

			# If the record was not inserted for some reason
			if dRes['inserted'] != 1 and dRes['replaced'] != 1:
				return None

			# Store the primary key if we didn't set it ourselves
			if self._dStruct['auto_primary']:
				self._dRecord[self._dStruct['primary']] = dRes['generated_keys'][0]

			# If changes are required
			if self._dStruct['changes']:

				# Get the current timestamp
				iTime = int(time())

				# Create the changes record
				dChanges = {
					self._dStruct['primary']: self._dRecord[self._dStruct['primary']],
					"last": iTime,
					"items": {
						str(iTime): {
							"old": None,
							"new": "inserted"
						}
					}
				}

				# If Changes requires fields
				if isinstance(self._dStruct['changes'], list):

					# If they weren't passed
					if not isinstance(changes, dict):
						raise ValueError('changes')

					# Else, add the extra fields
					for k in self._dStruct['changes']:
						dChanges['items'][str(iTime)][k] = changes[k]

				# Create changes record
				dRes = r \
					.db(self._dStruct['db']) \
					.table("%s_changes" % self._dStruct['table']) \
					.insert(dChanges) \
					.run(oCon)

		# Return the primary key
		return self._dRecord[self._dStruct['primary']]

	@classmethod
	def createMany(cls, records, replace=False, custom={}):
		"""Create Many

		Inserts multiple records at once, returning all their primary keys
		if auto_primary is true, else just returning the number of records
		inserted (or replaced if replace is set to True)

		Arguments:
			records {Record[]} -- A list of Record instances to insert
			replace {bool} -- Set to true to replace duplicate primary keys
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			mixed[]
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If changes are required
		if dStruct['changes']:
			raise RuntimeError('Tables with \'changes\' flag can\'t be inserted using createMany')

		# Initialise a list of raw records
		lRecords = []

		# Loop through the records
		for o in records:

			# If the record requires revisions
			if dStruct['revisions']:
				o._revision(True)

			# Add the record
			lRecords.append(o._dRecord)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Create a new record
			dRes = r \
				.db(dStruct['db']) \
				.table(dStruct['table']) \
				.insert(lRecords, conflict=(replace and 'replace' or 'error')) \
				.run(oCon)

			# If the record was not inserted for some reason
			if dRes['inserted'] == 0 and dRes['replaced'] == 0:
				return None

			# Go through each record and store the primary key if we didn't set
			#	it ourselves
			if dStruct['auto_primary']:
				for i in xrange(len(records)):
					records[i][dStruct['primary']] = dRes['generated_keys'][i]

				# Return the primary keys
				return dRes['generated_keys']

			# Else return how many records were replaced or inserted
			else:
				return dRes['inserted'] + dRes['replaced']

	def delete(self, changes=None):
		"""Delete

		Deletes the record represented by the instance

		Arguments:
			changes {dict} -- Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool
		"""

		# If the record lacks a primary key (never been created/inserted)
		if self._dStruct['primary'] not in self._dRecord:
			raise KeyError(self._dStruct['primary'])

		# Get a connection to the host
		with _with(self._dStruct['host']) as oCon:

			# Delete by primary key
			dRes = r \
				.db(self._dStruct['db']) \
				.table(self._dStruct['table']) \
				.get(self._dRecord[self._dStruct['primary']]) \
				.delete() \
				.run(oCon)

			# If there was an error
			if dRes['deleted'] != 1:
				return False

			# If changes are required
			if self._dStruct['changes']:

				# Get the current timestamp
				iTime = int(time())

				# Create the changes record
				dChanges = {
					"last": iTime,
					"items": {
						str(iTime): {
							"old": self._dRecord,
							"new": None
						}
					}
				}

				# If Changes requires fields
				if isinstance(self._dStruct['changes'], list):

					# If they weren't passed
					if not isinstance(changes, dict):
						raise ValueError('changes')

					# Else, add the extra fields
					for k in self._dStruct['changes']:
						dChanges['items'][str(iTime)][k] = changes[k]

				# Update the changes
				dRes = r \
					.db(self._dStruct['db']) \
					.table("%s_changes" % self._dStruct['table']) \
					.get(self._dRecord[self._dStruct['primary']]) \
					.update(dChanges) \
					.run(oCon)

			# Remove the primary key value so we can't delete again or save
			del self._dRecord[self._dStruct['primary']]

		# Return OK
		return True

	@classmethod
	def deleteGet(cls, _id=None, index=None, custom={}):
		"""Delete Get

		Deletes one or many records by primary key or index and returns how many
		were found/deleted

		Arguments:
			_id {mixed|mixed[]} -- The primary key(s) to delete or None for all
				records
			index {str} -- Used as the index instead of the primary key
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Return:
			int
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If changes are required
		if dStruct['changes']:
			raise RuntimeError('Tables with \'changes\' flag can\'t be deleted using deleteGet')

		# If an index is passed
		if index:

			# If the index doesn't exist
			if index not in dStruct['indexes']:
				raise KeyError('no index named "%s" in the tree' % index)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Create a cursor for all records
			oCur = r \
				.db(dStruct['db']) \
				.table(dStruct['table']) \

			# If there's no primary key, we want all records
			if _id is None:
				pass

			# If an index was passed, use get all
			elif index:
				oCur = oCur.get_all(_id, index=index)

			# If we are using the primary key
			else:

				# If we got multiple primary keys, use get all
				if isinstance(_id, (tuple,list)):
					oCur = oCur.get_all(*_id)

				# Else, use get for one record
				else:
					oCur = oCur.get(_id)

			# Delete the record(s)
			try:
				dRes = oCur.delete().run(oCon)

			# Catch operational errors
			except rerrors.ReqlOpFailedError as e:

				# An invalid index was passed
				if e.args[0][:5] == 'Index':
					raise KeyError('no index named "%s" in the table' % index)

				# Else, re-raise
				raise e

			# Return how many were deleted
			return dRes['deleted']

	@classmethod
	def exists(cls, _id, index=None, custom={}):
		"""Exists

		Returns true if the specified primary key or unique index value exists

		Arguments:
			_id {mixed} -- The primary key to check
			index {str} -- Used as the index instead of the primary key
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Use the get method to avoid duplicate code and check if anything was
		#	returned
		if not cls.get(_id, index=index, raw=[dStruct['primary']], custom=custom):
			return False

		# If anything was returned, the key exists
		return True

	# filter static method
	@classmethod
	def filter(cls, fields, raw=None, orderby=None, custom={}):
		"""Filter

		Finds records based on the specific fields and values passed

		Arguments:
			fields {dict} -- A dictionary of field names to the values they
				should match
			raw (bool|list} -- Return raw data (dict) for all or a set list of
				fields
			orderby {str|str[]} -- A field or fields to order the results by
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record[]|dict[]
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(sServer) as oCon:

			# Use the passed fields to generate the request
			oCur = r \
				.db(dStruct['db']) \
				.table(dStruct['table']) \
				.filter(obj)

			# If we only want specific fields
			if isinstance(raw, (tuple,list)):
				oCur = oCur.pluck(*raw).default(None)

			# If an order by arg was passed
			if orderby is not None:

				# If we need to orger by multiple fields
				if isinstance(orderby, (tuple,list)):
					oCur = oCur.order_by(*orderby)

				# If we need to order by
				elif isinstance(orderby, str):
					oCur = oCur.order_by(orderby)

				# Else we got something invalid
				else:
					raise ValueError('orderby', orderby)

			# Run the request
			itRes = oCur.run(oCon)

			# If we got no records back
			if not itRes:
				return []

			# If the user wants raw data
			if raw:
				return [d for d in itRes]

			# Create instances of the records
			return [cls(d, custom) for d in itRes]

	@classmethod
	def get(cls, _id=None, index=None, filter=None, match=None, raw=None, orderby=None, limit=None, custom={}):
		"""Get

		Returns records by primary key or index, can also be given an extra filter

		Arguments:
			_id {str|str[]} -- The primary key(s) to fetch from the table
			index {str} -- Index to use instead of primary key
			filter (dict} -- Additional filter
			match {tuple} -- Name/Match filter
			raw (bool|list} -- Return raw data (dict) for all or a set list of
				fields
			orderby {str|str[]} -- A field or fields to order the results by
			limit {int|tuple} -- The limit and possible starting point
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record|Record[]|dict|dict[]
		"""

		# By default we will return multiple records
		bMulti = True

		# By default there is no limit
		iLimitParams = 0

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If an index is passed
		if index:

			# If the index doesn't exist
			if index not in dStruct['indexes']:
				raise KeyError('no index named "%s" in the structure' % index)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Create a cursor for all records
			oCur = r \
				.db(dStruct['db']) \
				.table(dStruct['table'])

			# If there's no primary key, we want all records
			if _id == None:
				pass

			# Else, if there's an index
			elif index:

				# If we recieved a dict for the primary key
				if isinstance(_id, dict):

					# Between two points
					if 'between' in _id:
						oCur = oCur.between(_id['between'][0], _id['between'][1], index=index, right_bound='closed')

					# Greater than
					elif 'gt' in _id:
						oCur = oCur.between(_id['gt'], r.maxval, index=index, left_bound='open')

					# Greater than or equal
					elif 'gte' in _id:
						oCur = oCur.between(_id['gte'], r.maxval, index=index)

					# Less than
					elif 'lt' in _id:
						oCur = oCur.between(r.minval, _id['lt'], index=index)

					# Less than or equal
					elif 'lte' in _id:
						oCur = oCur.between(r.minval, _id['lte'], index=index, right_bound='closed')

					# Invalid request
					else:
						raise ValueError('_id', _id)

				# If we received a tuple
				elif isinstance(_id, tuple):

					# Look for None values
					iNone = -1
					for i in range(len(_id)):
						if _id[i] is None:
							if iNone != -1:
								raise ValueError('_id', 'only one None per tuple')
							iNone = i

					# If there us a None in the tuple, assume between and
					#	replace them with the min and max
					if iNone > -1:
						idMax = list(_id)
						idMin = list(_id)
						idMax[iNone] = r.maxval
						idMin[iNone] = r.minval
						oCur = oCur.between(idMin, idMax, index=index)

					# No None, pass as is
					else:
						oCur = oCur.get_all(_id, index=index)

				# If we get a list, it's a complex index
				elif isinstance(_id, list):
					oCur = oCur.get_all(r.args(_id), index=index)

				# Else, pass as is
				else:
					oCur = oCur.get_all(_id, index=index)

			# If we are using the primary key
			else:

				# If we recieved a dict for the primary key
				if isinstance(_id, dict):

					# Between two points
					if 'between' in _id:
						oCur = oCur.between(_id['between'][0], _id['between'][1], right_bound='closed')

					# Greater than
					elif 'gt' in _id:
						oCur = oCur.between(_id['gt'], r.maxval, left_bound='open')

					# Greater than or equal
					elif 'gte' in _id:
						oCur = oCur.between(_id['gte'], r.maxval)

					# Less than
					elif 'lt' in _id:
						oCur = oCur.between(r.minval, _id['lt'])

					# Less than or equal
					elif 'lte' in _id:
						oCur = oCur.between(r.minval, _id['lte'], right_bound='closed')

					# Invalid request
					else:
						raise ValueError('_id', _id)

				# If we received a tuple
				elif isinstance(_id, tuple):

					# Look for None values
					iNone = -1
					for i in range(len(_id)):
						if _id[i] is None:
							if iNone != -1:
								raise ValueError('_id', 'only one None per tuple')
							iNone = i

					# If there us a None in the tuple, assume between and
					#	replace them with the min and max
					if iNone > -1:
						idMax = list(_id)
						idMin = list(_id)
						idMax[iNone] = r.maxval
						idMin[iNone] = r.minval
						oCur = oCur.between(idMin, idMax)

					# No None, pass as is
					else:
						bMulti = False
						oCur = oCur.get(_id)

				# If we got multiple primary keys, use get all
				elif isinstance(_id, list):
					oCur = oCur.get_all(*_id)

				# If we want one record, change the multi flag, and use get
				else:
					bMulti = False
					oCur = oCur.get(_id)

			# If we want to filter the data further
			if filter:

				# If we got a list
				if isinstance(filter, (list,tuple)):
					oCur = oCur.filter(*filter)
				else:
					oCur = oCur.filter(filter)

			# If we want to filter by a match
			if match:
				oCur = oCur.filter(lambda doc: doc[match[0]].match(match[1]))

			# If we only want specific fields
			if isinstance(raw, (tuple,list)):
				oCur = oCur.pluck(*raw).default(None)

			# If an order by arg was passed
			if orderby is not None:

				# If we need to order by multiple fields
				if isinstance(orderby, (tuple,list)):
					for i in range(len(orderby)):
						if(orderby[i][0] == '!'):
							orderby[i] = r.desc(orderby[i][1:])
					oCur = oCur.order_by(*orderby)

				# If we need to order by
				elif isinstance(orderby, str):
					if(orderby[0] == '!'):
						orderby = r.desc(orderby[1:])
					oCur = oCur.order_by(orderby)

				# Else we got something invalid
				else:
					raise ValueError('orderby', orderby)

			# If we recieved a limit
			if limit is not None:

				# If we got an int, we are only limiting
				if isinstance(limit, int):
					iLimitParams = 1
					oCur = oCur.limit(limit)

					# If we only want one record
					if limit == 1:
						bMulti = False

				# If we got a tuple
				elif isinstance(limit, (list,tuple)):
					iLimitParams = 2
					oCur = oCur.skip(limit[0]).limit(limit[1])

					# If we only want one record
					if limit[1] == 1:
						bMulti = False

				# Else we got something invalid
				else:
					raise ValueError('limit', limit)

			# Run the request
			try:
				itRes = oCur.run(oCon)

			# Catch operational errors
			except rerrors.ReqlOpFailedError as e:

				# An invalid index was passed
				if e.args[0][:5] == 'Index':
					raise KeyError('no index named "%s" in the table' % index)

				# Else, re-raise
				raise e

			# If there's no data, return None or an empty list
			if not itRes:
				if bMulti: return []
				else: return None

			# If we are expecting a single record
			if (iLimitParams == 1 and limit == 1) or \
				(iLimitParams == 2 and limit[1] == 1):

				# If we got a list
				if isinstance(itRes, (tuple,list)):

					# If there's no data
					if not len(itRes):
						return None

					# Store the row
					dRow = itRes[0]

				# Else it's a cursor
				else:

					# Try to get one row
					try:
						dRow = itRes.next()
					except rnet.DefaultCursorEmpty as e:
						return None

				# If it's raw, don't instantiate it
				return (raw and dRow or cls(dRow, custom))

			# If the multi flag is still set
			if bMulti:

				# If Raw requested, return as is
				if raw:
					return [d for d in itRes]

				# Else create instances for each
				else:
					return [cls(d, custom) for d in itRes]

			# Else, one record requested
			else:
				return raw and itRes or cls(itRes, custom)

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

		# By default we will return multiple records
		bMulti = True

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Create a cursor for all records
			oCur = r \
				.db(dStruct['db']) \
				.table("%s_changes" % dStruct['table'])

			# If there's no primary key, we want all records
			if _id == None:
				pass

			# Else, we want specific keys
			else:

				# If we got multiple primary keys, use get all
				if isinstance(_id, (tuple,list)):
					oCur = oCur.get_all(*_id)

				# If we want one record, change the multi flag, and use get
				else:
					bMulti = False
					oCur = oCur.get(_id)

			# If an order by arg was passed
			if orderby is not None:

				# If we need to orger by multiple fields
				if isinstance(orderby, (tuple,list)):
					oCur = oCur.order_by(*orderby)

				# If we need to order by
				elif isinstance(orderby, str):
					oCur = oCur.order_by(orderby)

				# Else we got something invalid
				else:
					raise ValueError('orderby', orderby)

			# Run the request
			itRes = oCur.run(oCon)

			# If there's no data, return None or an empty list
			if not itRes:
				if bMulti: return []
				else: return None

			# If the multi flag is still set
			if bMulti:

				# Return all records
				return [d for d in itRes]

			# Else, one record requested
			else:
				return itRes

	@classmethod
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

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Append the org
			dRes = r \
				.db(dStruct['db']) \
				.table(dStruct['table']) \
				.get(_id) \
				.update({array: r.row[array].delete_at(index)}) \
				.run(oCon)

			# Return True if a record was changed
			return dRes['replaced'] == 1

		# Return False
		return False

	def save(self, replace=False, changes=None):
		"""Save

		Updates the record in the DB and returns true if anything has changed,
		or a new revision number of the record is revisionable

		Arguments:
			replace {bool} -- If true, replace all fields instead of updating
			changes {dict} -- Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool
		"""

		# If no fields have been changed, nothing to do
		if not self._dChanged:
			return False

		# If there is no primary key in the record
		if self._dStruct['primary'] not in self._dRecord:
			raise KeyError(self._dStruct['primary'])

		# Start by fetching the record
		oCur = r \
			.db(self._dStruct['db']) \
			.table(self._dStruct['table']) \
			.get(self._dRecord[self._dStruct['primary']])

		# If a replace was requested, or all fields have been changed
		if replace or (isinstance(self._dChanged, bool) and self._dChanged):
			oCur = oCur.replace(self._dRecord)

		# Else we are updating
		else:
			oCur = oCur.update({k:self._dRecord[k] for k in self._dChanged})

		# Get a connection to the host
		with _with(self._dStruct['host']) as oCon:

			# If revisions are required
			if self._dStruct['revisions']:

				# Store the old revision
				sRev = self._dRecord['_rev']

				# If updating the revision fails
				if not self._revision():
					return False

				# Use the primary key to fetch the record and return the rev
				dRecord = r \
					.db(self._dStruct['db']) \
					.table(self._dStruct['table']) \
					.get(self._dRecord[self._dStruct['primary']]) \
					.pluck(['_rev']) \
					.default(None) \
					.run(oCon)

				# If there's no such record
				if not dRecord:
					return False

				# If it is found, but the revisions don't match up
				if dRecord['_rev'] != sRev:
					raise Record_Base.RevisionException(self._dRecord[self._dStruct['primary']])

			# Update the record
			dRes = oCur.run(oCon)

			# If the record wasn't updated for some reason
			if dRes['replaced'] != 1:
				print(dRes)
				return False

			# If changes are required
			if self._dStruct['changes'] and changes != False:

				# Get the current timestamp
				iTime = int(time())

				# Create the changes record
				dChanges = {
					"last": iTime,
					"items": {
						str(iTime): self.generateChanges(
							self._dOldRecord,
							self._dRecord
						)
					}
				}

				# If Changes requires fields
				if isinstance(self._dStruct['changes'], list):

					# If they weren't passed
					if not isinstance(changes, dict):
						raise ValueError('changes')

					# Else, add the extra fields
					for k in self._dStruct['changes']:
						dChanges['items'][str(iTime)][k] = changes[k]

				# Update the changes
				dRes = r \
					.db(self._dStruct['db']) \
					.table("%s_changes" % self._dStruct['table']) \
					.get(self._dRecord[self._dStruct['primary']]) \
					.update(dChanges) \
					.run(oCon)

				# Reset the old record
				self._dOldRecord = None

		# Clear the changed fields flags
		self._dChanged = {}

		# Return OK
		return True

	@classmethod
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

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Try to create the table
			try:
				dRes = r \
					.db(dStruct['db']) \
					.table_create(dStruct['table'], primary_key=dStruct['primary']) \
					.run(oCon)

				# If for some reason the table wasn't created
				if 'tables_created' not in dRes or not dRes['tables_created']:
					return False

				# If indexes are specified for the record
				if dStruct['indexes']:

					# Loop through the indexes to get the name and fields
					for sName,mFields in dStruct['indexes'].items():

						# Start with the table
						oCur = r \
							.db(dStruct['db']) \
							.table(dStruct['table'])

						# No field means the name is the field
						if mFields is None:
							dRes = oCur.index_create(sName).run(oCon)

						# One field
						elif isinstance(mFields, str):
							dRes = oCur.index_create(sName, r.row[mFields]).run(oCon)

						# A list of fields
						elif isinstance(mFields, (tuple,list)):
							lFields = []
							for sField in mFields:
								lFields.append(r.row[sField])
							dRes = oCur.index_create(sName, lFields).run(oCon)

						# Invalid field value
						else:
							raise ValueError('indexes', str(mFields))

				# If changes are required
				if dStruct['changes']:

					# Try to create the table
					dRes = r \
						.db(dStruct['db']) \
						.table_create("%s_changes" % dStruct['table'], primary_key=dStruct['primary']) \
						.run(oCon)

			# The table already exists
			except rerrors.RqlRuntimeError as e:
				print(str(e))
				return False

		# Return OK
		return True

	@classmethod
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

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Try to drop the table
			try:
				dRes = r \
					.db(dStruct['db']) \
					.table_drop(dStruct['table']) \
					.run(oCon)

				# If for some reason the table wasn't dropped
				if 'tables_dropped' not in dRes or not dRes['tables_dropped']:
					return False

				# If changes are required
				if dStruct['changes']:

					# Try to delete the table
					dRes = r \
						.db(dStruct['db']) \
						.table_drop("%s_changes" % dStruct['table']) \
						.run(oCon)

			# If there's no such table
			except rerrors.RqlRuntimeError:
				return False

		# Return OK
		return True

	@classmethod
	def updateField(cls, field, value, _id=None, index=None, filter=None, custom={}):
		"""Updated Field

		Updates a specific field to the value for an ID, many IDs, or the entire
		table

		Arguments:
			field {str} -- The name of the field to update
			value {mixed} -- The value to set the field to
			_id {mixed} -- Optional ID(s) to filter by
			index {str} -- Optional name of the index to use instead of primary
			filter {dict} -- Optional filter list to decide what records get updated
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			uint -- Number of records altered
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the field doesn't exist
		if field not in dStruct['tree']:
			raise KeyError('field', field)

		# If an index is passed
		if index:

			# If the index doesn't exist
			if index not in dStruct['indexes']:
				raise KeyError('no index named "%s" in the structure' % index)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Create a cursor for all records
			oCur = r \
				.db(dStruct['db']) \
				.table(dStruct['table'])

			# If there's no primary key, nothing else to do with indexes or IDs
			if _id == None:
				pass

			# Else, if there's an index
			elif index:

				# If we recieved a dict for the primary key
				if isinstance(_id, dict):

					# Between two points
					if 'between' in _id:
						oCur = oCur.between(_id['between'][0], _id['between'][1], index=index, right_bound='closed')

					# Greater than
					elif 'gt' in _id:
						oCur = oCur.between(_id['gt'], r.maxval, index=index, left_bound='open')

					# Greater than or equal
					elif 'gte' in _id:
						oCur = oCur.between(_id['gte'], r.maxval, index=index)

					# Less than
					elif 'lt' in _id:
						oCur = oCur.between(r.minval, _id['lt'], index=index)

					# Less than or equal
					elif 'lte' in _id:
						oCur = oCur.between(r.minval, _id['lte'], index=index, right_bound='closed')

					# Invalid request
					else:
						raise ValueError('_id', _id)

				# If we received a tuple
				elif isinstance(_id, tuple):

					# Look for None values
					iNone = -1
					for i in range(len(_id)):
						if _id[i] is None:
							if iNone != -1:
								raise ValueError('_id', 'only one None per tuple')
							iNone = i

					# If there us a None in the tuple, assume between and
					#	replace them with the min and max
					if iNone > -1:
						idMax = list(_id)
						idMin = list(_id)
						idMax[iNone] = r.maxval
						idMin[iNone] = r.minval
						oCur = oCur.between(idMin, idMax, index=index)

					# No None, pass as is
					else:
						oCur = oCur.get_all(_id, index=index)

				# If we get a list, it's a complex index
				elif isinstance(_id, list):
					oCur = oCur.get_all(r.args(_id), index=index)

				# Else, pass as is
				else:
					oCur = oCur.get_all(_id, index=index)

			# If we are using the primary key
			else:

				# If we recieved a dict for the primary key
				if isinstance(_id, dict):

					# Between two points
					if 'between' in _id:
						oCur = oCur.between(_id['between'][0], _id['between'][1], right_bound='closed')

					# Greater than
					elif 'gt' in _id:
						oCur = oCur.between(_id['gt'], r.maxval, left_bound='open')

					# Greater than or equal
					elif 'gte' in _id:
						oCur = oCur.between(_id['gte'], r.maxval)

					# Less than
					elif 'lt' in _id:
						oCur = oCur.between(r.minval, _id['lt'])

					# Less than or equal
					elif 'lte' in _id:
						oCur = oCur.between(r.minval, _id['lte'], right_bound='closed')

					# Invalid request
					else:
						raise ValueError('_id', _id)

				# If we got multiple primary keys, use get all
				elif isinstance(_id, (tuple,list)):
					oCur = oCur.get_all(*_id)

				# If we want one record, change the multi flag, and use get
				else:
					oCur = oCur.get(_id)

			# If we want to filter the data further
			if filter:
				oCur = oCur.filter(filter)

			# Add the update and run the request
			try:
				dRes = oCur.update({field, value}).run(oCon)

			# Catch operational errors
			except rerrors.ReqlOpFailedError as e:

				# An invalid index was passed
				if e.args[0][:5] == 'Index':
					raise KeyError('no index named "%s" in the table' % index)

				# Else, re-raise
				raise e

			# Return the number of rows changed
			return dRes['replaced']

	@classmethod
	def uuid(cls, custom={}):
		"""UUID

		Returns a universal unique ID

		Arguments:
			custom {dict} -- Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			str
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get a connection to the host
		with _with(dStruct['host']) as oCon:

			# Get the UUID
			return r.uuid().run(oCon)

# Register the module with the Base
Record_Base.registerType('rethinkdb', sys.modules[__name__])
