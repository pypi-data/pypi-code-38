import json
import re

class Expectation(object):

	def __init__(self):
		self.expectation = {
			'httpRequest': {}
		}

	def __request_headers(self):
		if not 'headers' in self.expectation['httpRequest']:
			self.expectation['httpRequest']['headers'] = {}

	def __response_headers(self):
		if not 'headers' in self.expectation['httpResponse']:
			self.expectation['httpResponse']['headers'] = {}

	def __response(self):
		if not 'httpResponse' in self.expectation:
			self.expectation['httpResponse'] = {}

	def set_path(self, path):
		# replace {..}, e.g. {id} with regex
		path = re.sub(
			r'\{.*?\}',
			'[a-zA-Z0-9-]*',
			path
		)
		# remove '/' from the end of the path
		path = path.rstrip('\/')
		# enable to call with an optional '/' at the end of the path
		path += '.?'

		self.expectation['httpRequest']['path'] = path

	def set_method(self, method):
		self.expectation['httpRequest']['method'] = method.upper()

	def set_request_content_types(self, content_types):
		if len(content_types):
			self.__request_headers()
			content_types_regex = ''
			for content_type in content_types:
				if len(content_types_regex):
					content_types_regex += '|'
				content_types_regex += content_type
			self.expectation['httpRequest']['headers']['Content-Type'] = [ content_types_regex ]

	def set_request_schema(self, schema):
		self.expectation['httpRequest']['body'] = {
      		"type" : "JSON_SCHEMA",
      		"jsonSchema" : json.dumps(schema)
      	}

	def set_response_content_types(self, content_types):
		if len(content_types):
			self.__response_headers()
			self.expectation['httpResponse']['headers']['Content-Type'] = [ content_types[0] ]

	def set_response_headers(self, headers):
		for name, value in headers.items():
			self.__response_headers()
			self.expectation['httpResponse']['headers'][name] = [ value ]

	def set_status_code(self, statusCode):
		self.__response()
		self.expectation['httpResponse']['statusCode'] = int(statusCode)

	def set_response_body(self, body):
		self.__response()
		self.expectation['httpResponse']['body'] = json.dumps(body)

	def get(self):
		return self.expectation

	def get_json(self):
		return json.dumps(self.expectation)