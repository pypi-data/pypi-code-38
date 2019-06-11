# coding=utf8
""" REST Module

Provides interfaces for creating and maintaining REST servers
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

# Python imports
import json, re

# Pip imports
import bottle

# Framework imports
from . import Errors, Services, Sesh

# Method bytes
A		= 0xF
ALL		= 0xF
C		= 0x1
CREATE	= 0x1
D		= 0x2
DELETE	= 0x2
GET		= 0x4
POST	= 0x1
PUT		= 0x8
R		= 0x4
READ	= 0x4
U		= 0x8
UPDATE	= 0x8

class _Route(object):
	"""Route

	A callable class used to store rest routes in the server

	Extends:
		object
	"""

	def __init__(self, service, path, sesh, cors=None):
		"""Constructor (__init__)

		Initialises an instance of the route

		Arguments:
			service {str} -- The service we are routing to
			path {str} -- The path in the service we are routing to
			sesh {bool} -- True if the route requires a session
			cors {dict} -- Optionsl CORS values

		Returns:
			None
		"""
		self.service = service
		self.path = path
		self.sesh = sesh
		self.cors = cors

	def __call__(self):
		"""Call (__call__)

		Python magic method that allows the instance to be called

		Returns:
			str
		"""

		# Initialise the data
		mData = None

		# If CORS is enabled and the origin matches
		if self.cors and 'origin' in bottle.request.headers and self.cors.match(bottle.request.headers['origin']):
			bottle.response.headers['Access-Control-Allow-Origin'] = bottle.request.headers['origin']
			bottle.response.headers['Vary'] = 'Origin'

		# If the request is OPTIONS, set the headers and return nothing
		if bottle.request.method == 'OPTIONS':
			bottle.response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT, OPTIONS'
			bottle.response.headers['Access-Control-Max-Age'] = 1728000
			bottle.response.headers['Access-Control-Allow-Headers'] = 'Authorization,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type'
			bottle.response.headers['Content-Type'] = 'text/plain charset=UTF-8'
			bottle.response.headers['Content-Length'] = 0
			bottle.request.status = 204
			return ''

		# Set the return to JSON
		bottle.response.headers['Content-Type'] = 'application/json; charset=UTF-8'

		# If we got a Read request and the data is in the GET
		if bottle.request.method == 'GET' and 'd' in bottle.request.query:

			# Convert the GET and store the data
			try:
				mData = json.loads(bottle.request.query['d'])
			except Exception as e:
				return str(Services.Effect(error=(Errors.REST_REQUEST_DATA, '%s\n%s' % (bottle.request.query['d'], str(e)))))

		# Else we most likely got the data in the body
		else:

			# Make sure the request send JSON
			try:
				if bottle.request.headers['Content-Type'].lower() not in ('application/json; charset=utf8', 'application/json; charset=utf-8'):
					return str(Services.Effect(error=Errors.REST_CONTENT_TYPE))
			except KeyError:
				return str(Services.Effect(error=Errors.REST_CONTENT_TYPE))

			# Store the body, if it's too big we need to read it rather than
			#	use getvalue
			try: sBody = bottle.request.body.getvalue()
			except AttributeError as e: sBody = bottle.request.body.read()

			# Convert the body and store it
			try:
				if sBody: mData = json.loads(sBody)
			except Exception as e:
				return str(Services.Effect(error=(Errors.REST_REQUEST_DATA,'%s\n%s' % (sBody, str(e)))))

		# If the request should have sent a session
		if self.sesh:

			# Is there an Authorization token
			if 'Authorization' not in bottle.request.headers:
				bottle.response.status = 401
				return str(Services.Effect(error=Errors.REST_AUTHORIZATION))

			# Get the session from the Authorization token
			oSession = Sesh.load(bottle.request.headers['Authorization'])

			# If the session is not found
			if not oSession:
				bottle.response.status = 401
				return str(Services.Effect(error=Errors.REST_AUTHORIZATION))

			# Else, extend the session
			else:
				oSession.extend()

		else:
			oSession = None

		# Call the appropriate API method based on the HTTP/request method
		try:
			if bottle.request.method == 'DELETE':
				oEffect = Services.delete(self.service, self.path, mData, oSession)
			elif bottle.request.method == 'GET':
				oEffect = Services.read(self.service, self.path, mData, oSession)
			elif bottle.request.method == 'POST':
				oEffect = Services.create(self.service, self.path, mData, oSession)
			elif bottle.request.method == 'PUT':
				oEffect = Services.update(self.service, self.path, mData, oSession)
		except Services.EffectException as e:
			return str(e.args[0])

		# Return the effect as a string
		return str(oEffect)

class Config(object):
	"""Config class

	Represents configuration data for connecting to/loading services

	Extends:
		object
	"""

	def __contains__(self, service):
		"""__contains__

		Python magic method for checking a key exists in a dict like object

		Arguments:
			service {str} -- The service to check for

		Returns:
			bool
		"""
		return service in self.__services

	def __getitem__(self, service):
		"""__getitem__

		Python magic method for getting a key from a dict like object

		Arguments:
			service {str}: The service config to return

		Raises:
			KeyError

		Returns:
			mixed
		"""

		# If it's in services
		if service in self.__services:
			return self.__services[service].copy()

		# Else, throw an exception
		else:
			raise KeyError(service)

	def __init__(self, conf):
		"""Constructor

		Initialises the instance

		Arguments:
			conf {dict}: The configuration data for compiling the list of
				services and loaders

		Returns:
			Config
		"""

		# If we didn't get a dictionary for the service conf
		if not isinstance(conf, dict):
			raise ValueError('conf')

		# If we didn't get a list of services
		if 'services' not in conf:
			raise ValueError('conf.services')

		# Init the defaults if none are found
		if 'defaults' not in conf:
			conf['defaults'] = {}

		# Be default, port values are not modified
		iPortMod = 0

		# If there is a port modifier
		if 'port' in conf['default']:

			# Make sure it's an integer
			try:
				iPortMod = int(conf['default']['port'])
				del conf['default']['port']
			except ValueError:
				raise ValueError('conf.default.port must be an int')

		# Initialise the list of services
		self.__services = {}

		# Loop through the list of services
		for s in conf['services']:

			# If the service doesn't point to a dict
			if not isinstance(conf['services'][s], dict):
				raise ValueError('conf.services.%s' % s)

			# Start with the default values
			dParts = conf['default'].copy()

			# Then add the service values
			dParts.update(conf['services'][s])

			# If we have no port
			if 'port' not in dParts:

				# But we have a modifier, assume we add to 80
				if iPortMod: dParts['port'] = 80 + iPortMod

			# Else add the modifier to the port passed
			else:
				dParts['port'] += iPortMod

			# Set defaults for any missing parts
			if not dParts['protocol']: dParts['protocol'] = 'http'
			if not dParts['domain']: dParts['domain'] = 'localhost'
			if 'path' not in dParts: dParts['path'] = ''
			else: dParts['path'] = '%s/' % str(dParts['path'])

			# Store the parts for the service
			self.__services[s] = dParts.copy()

			# Generate a URL from the parts and store it
			self.__services[s]['url'] = '%s://%s%s/%s' % (
				dParts['protocol'],
				dParts['domain'],
				'port' in dParts and ":%d" % dParts['port'] or '',
				dParts['path']
			)

			# If we still have no port, default to 80
			if 'port' not in self.__services[s]:
				self.__services[s]['port'] = 80

		# If there are loaders in the conf
		if 'loaders' in conf:

			# Loop through each loader
			for l in conf['loaders']:

				# If we didn't get a dict
				if not isinstance(conf['loaders'][l], dict):
					raise ValueError('conf.loaders.%s' % l)

				# Copy the parts
				dParts = conf['loaders'][l].copy()

				# If no port is set for the loader
				if 'port' not in dParts:

					# But we have a modifier, assume we add to 80
					if iPortMod: dParts['port'] = 80 + iPortMod

				# Else add the modifier to the port passed
				else:
					dParts['port'] += iPortMod

				# Store the parts for the loader
				self.__services[l] = dParts.copy()

	def __iter__(self):
		"""__iter__

		Python magic method to return an iterator for the instance

		Returns:
			iterator
		"""
		return iter(self.__services)

	def __str__(self):
		"""__str__

		Python magic method to return a string for the instance

		Returns:
			str
		"""
		return str(self.__services)

	def keys(self):
		"""services

		Returns the keys (services) in the instance

		Returns:
			str[]
		"""
		return self.__services.keys()

# Server class
class Server(bottle.Bottle):
	"""Server

	Creates an HTTP server for use with REST requests

	Extends:
		bottle.Bottle
	"""

	def __init__(self, routes, service = '', cors=None):
		"""Constructor (__init__)

		Instantiates the server instance

		Arguments:
			routes {dict|list} -- Routes to the server
			service {str} -- The service to use if none exists in a route
			cors {str} -- The regex to identify allowed domains

		Returns:
			None
		"""

		# Call the parent constructor first so the object is setup
		super(Server, self).__init__()

		# If cors
		if cors: cors = re.compile(cors)

		# If the routes are passed as a dict
		if isinstance(routes, dict):

			# Create a new list for the routes
			l = []

			# Convert them using the key as the uri
			for k,v in routes.items():
				v['uri'] = k
				l.append(v)
			routes = l

		# Go through each route
		for d in routes:

			# If there's no method passed, assume all
			if 'methods' not in d:
				lMethods = ['DELETE', 'GET', 'POST', 'PUT']

			# Else, use the bits to figure out the methods
			else:
				lMethods = []
				if d['methods'] & CREATE: lMethods.append('POST')
				if d['methods'] & DELETE: lMethods.append('DELETE')
				if d['methods'] & READ: lMethods.append('GET')
				if d['methods'] & UPDATE: lMethods.append('PUT')

			# Add OPTIONS is CORS is enabled
			if cors: lMethods.append('OPTIONS')

			# If the service is missing, use the default
			if 'service' not in d:
				d['service'] = service

			# If the session value is not passed, assume false
			if 'session' not in d:
				d['session'] = False

			# If the path is not passed, generate it from the uri
			if 'path' not in d:
				d['path'] = d['uri'][1:]

			# Create and add the route to the server
			self.route(
				d['uri'],
				lMethods,
				_Route(d['service'], d['path'], d['session'], cors)
			)

	# run method
	def run(self, server="gunicorn", host="127.0.0.1", port=8080,
			reloader=False, interval=1, quiet=False, plugins=None,
			debug=None, maxfile=20971520, **kargs):
		"""Run

		Overrides Bottle's run to default gunicorn and other fields

		Arguments:
			server {str} -- Server adapter to use
			host {str} -- Server address to bind to
			port {int} -- Server port to bind to
			reloader {bool} -- Start auto-reloading server?
			interval {int} -- Auto-reloader interval in seconds
			quiet {bool} -- Suppress output to stdout and stderr?
			plugins {list} -- List of plugins to the server
			debug {bool} -- Debug mode
			maxfile {int} -- Maximum size of requests

		Returns:
			None
		"""

		# Set the max file size
		bottle.BaseRequest.MEMFILE_MAX = maxfile

		# Call bottle run
		bottle.run(
			app=self, server=server, host=host, port=port, reloader=reloader,
			interval=interval, quiet=quiet, plugins=plugins, debug=debug,
			**kargs
		)
