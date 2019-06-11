# coding=utf8
""" Services Module

Tools to create and communicate with Micro Services
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

# Python imports
from hashlib import sha1
import json
from time import time
from datetime import datetime

# Pip imports
import requests

# Framework imports
from . import Errors, Sesh

__mbVerbose = False
"""Verbose Flag"""

__mdRegistered = {}
"""Registered Services"""

__funcToRequest = {
	'create': [requests.post, 'POST'],
	'delete': [requests.delete, 'DELETE'],
	'read': [requests.get, 'GET'],
	'update': [requests.put, 'PUT']
}
"""Map functions to REST types"""

__msSalt = None
"""Internal Key Salt"""

def __request(service, action, path, data, sesh=None):
	"""Request

	Internal method to convert REST requests into HTTP requests

	Arguments:
		service {str} -- The service we are requesting data from
		action {str} -- The action to take on the service
		path {str} -- The path of the request
		data {mixed} -- The data being sent with the request
		sesh {Sesh._Session} -- The optional session to pass with the request

	Raises:
		ServiceException

	Return:
		Effect
	"""

	# If we have a registered service
	if service in __mdRegistered:

		# If the service is locally loaded
		if 'instance' in __mdRegistered[service]:

			# If verbose requested
			if __mbVerbose: print('%s: Calling %s.%s("%s", %s)' % (str(datetime.now()), service, action, path, str(data)))

			# Directly call the action
			oEffect = getattr(__mdRegistered[service]['instance'], action)(
				path, data, sesh
			)

		# Else if the service is running elsewhere
		else:

			try: __funcToRequest[action]
			except KeyError: Effect(error=(Errors.SERVICE_ACTION, action))

			# Generate the URL to reach the service
			sURL = __mdRegistered[service]['url'] + path

			# If verbose requested
			if __mbVerbose:
				print('%s: Calling %s %s %s)' % (str(datetime.now()), __funcToRequest[action][1], sURL, str(data)))

			# Convert the data to JSON
			sData = json.dumps(data)

			# Create the headers
			dHeaders = {
				'Content-Type': 'application/json; charset=utf-8',
				'Content-Length': str(len(sData))
			}

			# If we have a session, add the ID to the headers
			if sesh:
				dHeaders['Authorization'] = sesh.id()

			# Try to make the request and store the response
			try:
				oRes = __funcToRequest[action][0](sURL, data=sData, headers=dHeaders)

				# If the request wasn't successful
				if oRes.status_code != 200:
					return Effect(error=(Errors.SERVICE_STATUS, '%d: %s' % (oRes.status_code, oRes.content)))

				# If we got the wrong content type
				if oRes.headers['Content-Type'].lower() != 'application/json; charset=utf-8':
					return Effect(error=(Errors.SERVICE_CONTENT_TYPE, '%s' % oRes.headers['content-type']))

			# If we couldn't connect to the service
			except requests.ConnectionError as e:
				return Effect(error=(Errors.SERVICE_UNREACHABLE, str(e)))

			# Else turn the content into an Effect and return it
			oEffect = Effect.fromJSON(oRes.text)

			print('As Effect: %s' % str(oEffect))

		# If verbose requested
		if __mbVerbose:	print('%s: Returning %s\n' % (str(datetime.now()), str(oEffect)))

		# Return the effect of the request
		return oEffect

	# Service not registered
	else:
		raise Effect(error=(Errors.SERVICE_NOT_REGISTERED, service))

def create(service, path, data, sesh=None):
	"""Create

	Make a POST request

	Arguments:
		service {str} -- The service to call
		path {str} -- The path on the service
		data {mixed} -- The data to pass to the request
		sesh {Sesh._Session}: The optional session to send with the request

	Returns:
		Effect
	"""
	return __request(service, 'create', path, data, sesh)

def delete(service, path, data, sesh=None):
	"""Delete

	Make a DELETE request

	Arguments:
		service {str} -- The service to call
		path {str} -- The path on the service
		data {mixed} -- The data to pass to the request
		sesh {Sesh._Session}: The optional session to send with the request

	Returns:
		Effect
	"""
	return __request(service, 'delete', path, data, sesh)

def internalKey(key = None):
	"""Internal Key

	Generates or validates an internal key so services can communicate with
	each other

	Arguments:
		key {str} -- Passed to validate a key

	Returns:
		bool
	"""

	# Pull in salt
	global __msSalt

	# Generate a timestamp
	iTime = int(time())

	# If no key was passed
	if key is None:

		# Generate a timestamp and store it as a string
		sTime = str(iTime)

		# Generate a sha1 from the salt and parts of the time
		sSHA1 = sha1(sTime[5:].encode('utf-8') + __msSalt.encode('utf-8') + sTime[:5].encode('utf-8')).hexdigest()

		# Generate a key using the sha1 and the time
		return sSHA1 + ':' + sTime

	# If the key was passed
	else:
		try:
			# Split the key into sha1 and timestamp
			sSHA1_, sTime = key.split(':')

			# If the time is not close enough
			if iTime - int(sTime) > 5:
				return False

			# Generate a sha1 from the salt and parts of the time
			sSHA1 = sha1(sTime[5:].encode('utf-8') + __msSalt.encode('utf-8') + sTime[:5].encode('utf-8')).hexdigest()

			# If the sha1s match return true
			return sSHA1 == sSHA1_

		# If something went wrong, return false
		except Exception:
			return False

def read(service, path, data, sesh=None):
	"""Read

	Make a GET request

	Arguments:
		service {str} -- The service to call
		path {str} -- The path on the service
		data {mixed} -- The data to pass to the request
		sesh {Sesh._Session}: The optional session to send with the request

	Returns:
		Effect
	"""
	return __request(service, 'read', path, data, sesh)

def register(services, restconf, salt):
	"""Register

	Takes a dictionary of services to their instances, or None for remote
	services which will be found via the config

	Arguments:
		services {dict} -- Services being registered
		restconf {dict} -- Configuration variables for remote services
		salt {str} -- The salt used for internal key generation

	Raises:
		ValueError

	Returns:
		None
	"""

	# Pull in the global salt variable and set it
	global __msSalt
	__msSalt = salt

	# If we didn't get a dictionary
	if not isinstance(services, dict):
		raise ValueError('services')

	# Loop through the list of services to register
	for k,v in services.items():

		# If verbose requested
		if __mbVerbose: print('Registering service "%s": ' % str(k), end='')

		# If we received a local instance
		if isinstance(v, Service):

			# Store it
			__mdRegistered[k] = {"instance":v}

			# If verbose requested
			if __mbVerbose:	print('instance')

			# Call the services initialise method
			v.initialise()

		# Else the service is remote
		elif v is None:

			# Make sure we have the service
			if k not in restconf:
				raise ValueError('services.%s' % k)

			# Store it
			__mdRegistered[k] = {"url":restconf[k]['url']}

			# If verbose mode is on
			if __mbVerbose:	print('%s' % __mdRegistered[k]['url'])

		# Else, the value is invalid
		else:
			raise ValueError('services.%s' % str(k))

def update(service, path, data, sesh=None):
	"""Update

	Make a PUT request

	Arguments:
		service {str} -- The service to call
		path {str} -- The path on the service
		data {mixed} -- The data to pass to the request
		sesh {Sesh._Session}: The optional session to send with the request

	Returns:
		Effect
	"""
	return __request(service, 'update', path, data, sesh)

def verbose(flag=True):
	"""Verbose

	Puts Services in verbose mode for easy tracking of requests

	Arguments:
		flag {bool} -- defaults to True

	Returns:
		None
	"""

	global __mbVerbose

	if __mbVerbose and not flag:
		print('Service verbose mode will be turned off')

	__mbVerbose = flag

	if __mbVerbose:
		print('Service verbose mode has been turned on')

class Effect(object):
	"""Effect

	Represents a standard result from any/all requests

	Extends:
		object
	"""

	def __init__(self, data = None, error = None, warning = None):
		"""Constructor

		Initialises a new Effect instance

		Arguments:
			data {mixed} -- If a request returns data this should be set
			error {mixed} -- If a request has an error, this can be filled with
				a code and message string
			warning {mixed} -- If a request returns a warning this should be set

		Raises:
			ValueError

		Returns:
			Effect
		"""

		# If there's data, store it as is
		if not data is None:
			self.data = data

		# If there's an error, figure out what type
		if not error is None:

			# If we got an int, it's a code with no message string
			if isinstance(error, int):
				self.error = {"code": error, "msg": ''}

			# If we got a string, it's a message with no code
			elif isinstance(error, str):
				self.error = {"code": 0, "msg": error}

			# If it's a tuple, 0 is a code, 1 is a message
			elif isinstance(error, tuple):
				self.error = {"code": error[0], "msg": error[1]}

			# If we got a dictionary, assume it's already right
			elif isinstance(error, dict):
				self.error = error

			# If we got an exception
			elif isinstance(error, Exception):

				# If we got another Effect in the Exception, store the error from it
				if isinstance(error.args[0], Effect):
					self.error = error.args[0].error

				# Else, try to pull out the code and message
				else:
					self.error = {"code": error.args[0], "msg": ''}
					if len(error.args) > 1: dErr['msg'] = error.args[1]

			# Else, we got something invalid
			else:
				raise ValueError('error')

		# If there's a warning, store it as is
		if not warning is None:
			self.warning = warning

	def __str__(self):
		"""str

		Python magic method to return a string from the instance

		Returns:
			str
		"""

		# Create a temp dict
		dRet = {}

		# If there's data
		try: dRet['data'] = self.data
		except AttributeError: pass

		# If there's an error
		try: dRet['error'] = self.error
		except AttributeError: pass

		# If there's a warning
		try: dRet['warning'] = self.warning
		except AttributeError: pass

		# Convert the dict and return it
		return json.dumps(dRet)

	def dataExists(self):
		"""Data Exists

		Returns True if there is data in the Effect

		Returns:
			bool
		"""
		try: return self.data != None
		except AttributeError: return False

	def errorExists(self):
		"""Error Exists

		Returns True if there is an error in the Effect

		Returns:
			bool
		"""
		try: return self.error != None
		except AttributeError: return False

	@classmethod
	def fromDict(cls, val):
		"""From Dict

		Converts a dict back into an Effect

		Arguments:
			val {dict} -- A valid dict

		Returns:
			Effect
		"""

		# Create a new instance
		o = cls()

		# If there's data
		try: o.data = val['data']
		except KeyError: pass

		# If there's an error
		try: o.error = val['error']
		except KeyError: pass

		# If there's a warning
		try: o.warning = val['warning']
		except KeyError: pass

		# Return the instance
		return o

	@classmethod
	def fromJSON(cls, val):
		"""From JSON

		Tries to convert a string made from str() back into an Effect

		Arguments:
			val {str} -- A valid JSON string

		Returns:
			Effect
		"""

		# Try to convert the string to a dict
		try: d = json.loads(val)
		except ValueError as e: raise ValueError('val', str(e))
		except TypeError as e: raise ValueError('val', str(e))

		# Return the fromDict result
		return cls.fromDict(d)

	def warningExists(self):
		"""Warning Exists

		Returns True if there is a warning in the Effect

	Returns:
			bool
		"""
		try: return self.warning != None
		except AttributeError: return False

class EffectException(Exception):
	"""Effect Exception

	Stupid python won't let you raise anything that doesn't extend BaseException

	Extends:
		Exception
	"""

	def __init__(self, effect):
		"""Constructor

		Dumb dumb python

		Arguments:
			effect {Effect} -- The Effect to throw/raise

		Returns:
			EffectException
		"""

		# If we didn't get a proper Effect
		if not isinstance(effect, Effect):
			raise ValueError('effect')

		# Pass to the parent
		super().__init__(effect)

class Service(object):
	"""Service

	The object to build all Services from

	Extends:
		object
	"""

	def create(self, path, data, sesh=None):
		"""Create

		Create a new object

		Arguments:
			path {str} -- The path passed to the request
			data {mixed} -- The data sent with the request
			sesh {Sesh._Session} -- The session passed to the request

		Return:
			Effect
		"""

		# Generate the method name from the URI
		sMethod = self.pathToMethod(path, '_create')

		# Try to call the method
		try:
			f = getattr(self, sMethod)

		# Method doesn't exist, URI is invalid
		except AttributeError as e:

			# If the method wasn't found
			if "'%s'" % sMethod in e.args[0]:
				return Effect(error=(Errors.SERVICE_NO_SUCH_NOUN, 'POST %s' % path))
			else:
				raise

		# Effect thrown
		except Effect as e:
			return e

		# Call the method
		if sesh: return f(data, sesh)
		else: return f(data)

	def delete(self, path, data, sesh=None):
		"""Delete

		Delete an existing object

		Arguments:
			path {str} -- The path passed to the request
			data {mixed} -- The data sent with the request
			sesh {Sesh._Session} -- The session passed to the request

		Return:
			Effect
		"""

		# Generate the method name from the URI
		sMethod = self.pathToMethod(path, '_delete')

		# Try to call the method
		try:
			f = getattr(self, sMethod)

		# Method doesn't exist, URI is invalid
		except AttributeError as e:

			# If the method wasn't found
			if "'%s'" % sMethod in e.args[0]:
				return Effect(error=(Errors.SERVICE_NO_SUCH_NOUN, 'DELETE %s' % path))
			else:
				raise

		# Effect thrown
		except Effect as e:
			return e

		# Call the method
		if sesh: return f(data, sesh)
		else: return f(data)

	def initialise(self):
		"""Initialise

		Initialises the instance and returns itself for chaining

		Returns:
			Service
		"""
		return self

	@classmethod
	def install(cls):
		"""Install

		Installs any necessary DBs, configs, etc, needed by the Service when it
		is first installed

		Raises:
			NotImplementedError

		Returns:
			bool
		"""
		raise NotImplementedError('Must implement the "install" method')

	def read(self, path, data = {}, sesh=None):
		"""Read

		Read an existing object

		Arguments:
			path {str} -- The path passed to the request
			data {mixed} -- The data sent with the request
			sesh {Sesh._Session} -- The session passed to the request

		Return:
			Effect
		"""

		# Generate the method name from the URI
		sMethod = self.pathToMethod(path, '_read')

		# Try to call the method
		try:
			f = getattr(self, sMethod)

		# Method doesn't exist, URI is invalid
		except AttributeError as e:

			# If the method wasn't found
			if "'%s'" % sMethod in e.args[0]:
				return Effect(error=(Errors.SERVICE_NO_SUCH_NOUN, 'GET %s' % path))
			else:
				raise

		# Effect thrown
		except Effect as e:
			return e

		# Call the method
		if sesh: return f(data, sesh)
		else: return f(data)

	def update(self, path, data, sesh=None):
		"""Update

		Update an existing object

		Arguments:
			path {str} -- The path passed to the request
			data {mixed} -- The data sent with the request
			sesh {Sesh._Session} -- The session passed to the request

		Return:
			Effect
		"""

		# Generate the method name from the URI
		sMethod = self.pathToMethod(path, '_update')

		# Try to call the method
		try:
			f = getattr(self, sMethod)

		# Method doesn't exist, URI is invalid
		except AttributeError as e:

			# If the method wasn't found
			if "'%s'" % sMethod in e.args[0]:
				return Effect(error=(Errors.SERVICE_NO_SUCH_NOUN, 'PUT %s' % path))
			else:
				raise

		# Effect thrown
		except Effect as e:
			return e

		# Call the method
		if sesh: return f(data, sesh)
		else: return f(data)

	@staticmethod
	def pathToMethod(path, append=''):
		"""Path to Method

		Takes a path and converts it to the standard naming for Service methods

		Arguments:
			path {str} -- The path to parse
			append {str} -- If set, appended to method name

		Returns:
			str
		"""
		sRet = ''
		iLen = len(path)
		i = 0
		while i < iLen:
			if(path[i] in ['/', '_']):
				i += 1
				sRet += path[i].upper()
			else:
				sRet += path[i]
			i += 1
		return sRet + append
