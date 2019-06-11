# coding: utf-8
"""
	ModelMaker SDK
"""

from __future__ import absolute_import

import datetime
import json
import mimetypes
from multiprocessing.pool import ThreadPool
import os
import re
import tempfile
import logging
# python 2 and python 3 compatibility library
import six
from six.moves.urllib.parse import quote

from modelmaker.client.configuration import Configuration
from modelmaker.client import rest
from modelmaker.config.auth import authorize_by_token

logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/Api')
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))

class ApiClient(object):
	"""Generic API client for all api.

	:param configuration: .Configuration object for this client
	:param header_name: a header to pass when making calls to the API.
	:param header_value: a header value to pass when making calls to
		the API.
	:param cookie: a cookie to include in the header when making calls
		to the API
	"""

	PRIMITIVE_TYPES = (float, bool, bytes, six.text_type) + six.integer_types
	NATIVE_TYPES_MAPPING = {
		'int': int,
		'long': int if six.PY3 else long,  # noqa: F821
		'float': float,
		'str': str,
		'bool': bool,
		'date': datetime.date,
		'datetime': datetime.datetime,
		'object': object,
	}

	def __init__(self, configuration=None, header_name=None, header_value=None,
				 cookie=None):
		if configuration is None:
			configuration = Configuration()
		self.configuration = configuration

		self.pool = ThreadPool()
		self.rest_client = rest.RESTClientObject(configuration)
		self.default_headers = {}
		if header_name is not None:
			self.default_headers[header_name] = header_value
		self.cookie = cookie
		# Set default User-Agent.
		#self.user_agent = 'Swagger-Codegen/1.0.0/python'

	def __del__(self):
		self.pool.close()
		self.pool.join()

	@property
	def user_agent(self):
		"""User agent for this API client"""
		return self.default_headers['User-Agent']

	@user_agent.setter
	def user_agent(self, value):
		self.default_headers['User-Agent'] = value

	def set_default_header(self, header_name, header_value):
		self.default_headers[header_name] = header_value

	def __call_api(
		self, resource_path, method, header_params=None, 
		body=None, auth_settings=None):

		config = self.configuration
		# header parameters
		header_params = header_params or {}
		header_params.update(self.default_headers)
		if self.cookie:
			header_params['Cookie'] = self.cookie

		# request url
		url = self.configuration.host + resource_path
		query_params=None
		post_params=None
		_preload_content=None
		_request_timeout=None
		# perform request and return response
		response_data = self.request(
			method, url, query_params=query_params, headers=header_params,
			post_params=post_params, body=body,
			_preload_content=_preload_content,
			_request_timeout=_request_timeout)
		self.last_response = response_data
		return response_data

	def call_api(self, resource_path, method,
				 header_params=None,body=None, auth_settings=None):
		http_reponse = self.__call_api(resource_path, method,
								header_params, body, auth_settings)
		data = str(http_reponse.data,encoding="utf-8")
		data = eval(data)
		#data = json.loads(http_reponse.data.decode('utf-8'))
		if data.get('errorCode'):
			if data['errorCode'] == 1002 or data['errorCode'] == 1003:
				LOGGER.info("Refresh the token,because token is invalid or out of indate")
				token = authorize_by_token(username=self.configuration.username,
													password=self.configuration.password,
													endpoint=self.configuration.host,
													verify_ssl=self.configuration.verify_ssl)
				self.set_default_header("Auth-Token", token)
				http_reponse = self.__call_api(resource_path, method,
								header_params, body, auth_settings)
				data = json.loads(http_reponse.data.decode('utf-8'))
				if data.get('errorCode'):
					LOGGER.info(data)
					raise Exception("Api call error!")
			elif data['errorCode'] == 102009 or data['errorCode'] == 101009:
				pass
			else:
				LOGGER.info(data)
				raise Exception("Api call error!")
		return http_reponse
#		  else:
#			   pass
#			   thread = self.pool.apply_m_async(self.__call_api, (resource_path,
#											 method, path_params, query_params,
#											 header_params, body,
#											 post_params, files,
#											 response_type, auth_settings,
#											 _return_http_data_only,
#											 collection_formats,
#											 _preload_content, _request_timeout))
#		 return 1
	def request(self, method, url, query_params=None, headers=None,
				post_params=None, body=None, _preload_content=True,
				_request_timeout=None):
		"""Makes the HTTP request using RESTClient."""
		if method == "GET":
			return self.rest_client.GET(url,
						query_params=query_params,
						_preload_content=_preload_content,
						_request_timeout=_request_timeout,
						headers=headers)
		elif method == "HEAD":
			return self.rest_client.HEAD(url,
						query_params=query_params,
						_preload_content=_preload_content,
						_request_timeout=_request_timeout,
						headers=headers)
		elif method == "OPTIONS":
			return self.rest_client.OPTIONS(url,
						query_params=query_params,
						headers=headers,
						post_params=post_params,
						_preload_content=_preload_content,
						_request_timeout=_request_timeout,
						body=body)
		elif method == "POST":
			return self.rest_client.POST(url,
						query_params=query_params,
						headers=headers,
						post_params=post_params,
						_preload_content=_preload_content,
						_request_timeout=_request_timeout,
						body=body)
		elif method == "PUT":
			return self.rest_client.PUT(url,
						query_params=query_params,
						headers=headers,
						post_params=post_params,
						_preload_content=_preload_content,
						_request_timeout=_request_timeout,
						body=body)
		elif method == "PATCH":
			return self.rest_client.PATCH(url,
						query_params=query_params,
						headers=headers,
						post_params=post_params,
						_preload_content=_preload_content,
						_request_timeout=_request_timeout,
						body=body)
		elif method == "DELETE":
			return self.rest_client.DELETE(url,
						query_params=query_params,
						headers=headers,
						_preload_content=_preload_content,
						_request_timeout=_request_timeout,
						body=body)
		else:
			raise ValueError( "http method must be `GET`, `HEAD`, `OPTIONS`,"
			 " `POST`, `PATCH`, `PUT` or `DELETE`."
			)


	def select_header_accept(self, accepts):
		"""Returns `Accept` based on an array of accepts provided.

		:param accepts: List of headers.
		:return: Accept (e.g. application/json).
		"""
		if not accepts:
			return

		accepts = [x.lower() for x in accepts]

		if 'application/json' in accepts:
			return 'application/json'
		else:
			return ', '.join(accepts)

	def select_header_content_type(self, content_types):
		"""Returns `Content-Type` based on an array of content_types provided.

		:param content_types: List of content-types.
		:return: Content-Type (e.g. application/json).
		"""
		if not content_types:
			return 'application/json'

		content_types = [x.lower() for x in content_types]

		if 'application/json' in content_types or '*/*' in content_types:
			return 'application/json'
		else:
			return content_types[0]

