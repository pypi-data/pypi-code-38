from __future__ import absolute_import

import inspect
from marshmallow import Schema, fields
from lantern_sl.utils.dynamo import unique_id
from lantern_sl.utils.time import current_ts
from lantern_sl.utils.json import json_decimal_to_float
from lantern_sl.utils.request import http_response, http_error
from lantern_sl.serverless.base import ServerlessBase
from lantern_sl.controllers.dynamo_controller import (DynamoController, ExceptionInvalidDynamoControllerNotFound)

class ExceptionParamsError(Exception):
	pass

class ExceptionSerializerValidator(Exception):
	pass

FILTER_FIELDS = ["key", "value", "order_by", "limit", "next", "index", "order_type", "filter_expression", "invert_result"]
class FilterScheme(Schema):
	key = fields.Str(required=True)
	value = fields.Str(required=True)
	order_by= fields.Str()
	limit = fields.Number()
	next = fields.Str()
	index = fields.Str()
	order_type = fields.Str()
	filter_expression = fields.Raw()
	condition_expression = fields.Raw()
	invert_result = fields.Boolean()


class ServerlessCrudBase(ServerlessBase):
	serializer = None # required to be implemented
	controller = None
	auto_add_id = True

	def __init__(self, event, context, table_name, debug=False):
		if table_name:
			self.table_name = table_name
		elif "DYNAMODB_TABLE" in context:
			self.table_name = context["DYNAMODB_TABLE"]
		self.json_response = self._get_json_response(event)
		self.controller = DynamoController(table_name=self.table_name, debug=debug)
		return super(ServerlessCrudBase, self).__init__(event, context)
	
	def verify_serializer_defined(self):
		if not self.serializer:
			raise Exception("serializer property is required! (property or parameter)")
		if not inspect.isclass(self.serializer):
			raise Exception("Serializer should be a class extending marshmallow.Schema")
		if not issubclass(self.serializer, Schema):
			raise Exception("Serializer should be a class extending marshmallow.Schema")
		return True
	
	def verify_data_serialized(self, data, many=False, partial=None):
		_serializer = self.serializer()
		errors = _serializer.validate(data, many=many, partial=partial)
		if errors:
			raise Exception("Serializer Errors: {}".format(errors))
		return True
		
	def _get_json_response(self, event):
		""" json_response in root event or inside 'crud' node """
		crud_node = event.get("crud", None)
		if crud_node:
			json_response = crud_node.get("json_response", None)
		else:
			json_response = event.get("json_response", False)
		return json_response
	
	def get_primary_keys(self, use_event_if_none=True, error_on_empty=False):
		""" find the primary node in the root node or inside 'crude' node """
		node = self.event
		AVAILABLE_NODES = ["crud", "query", "body"]
		for n in AVAILABLE_NODES:
			if node.get(n,None):
				node = node.get(n)
				break
		primary_keys = None
		if not primary_keys:
			primary_keys = node.get("primary_keys",None)
		if not primary_keys and "method" in self.event and self.event["method"].upper() in ["DELETE", "GET"]: # params by url
			primary_keys = node
		if not primary_keys and use_event_if_none:
			return self.event
		if not primary_keys and error_on_empty:
			raise ExceptionParamsError("'primary_keys' not found in event root neither in 'crud' node")
		return primary_keys
	
	def get_data(self, use_event_if_none=True, error_on_empty=False):
		""" find data data node in root or crud """
		""" find data data node in root or crud """
		# GET
		http_method = self.event.get('method', None)
		crud_node = self.event.get("crud", None)
		data_node = self.event.get("data", None)
		data = None
		if http_method:
			if http_method == 'GET':
				data = self.event.get('query', None)
			elif http_method == 'POST':
				data = self.event.get('body', None)
			elif http_method == 'PUT':
				data = self.event.get('body').get('data', None)
		if not data and crud_node:
			data = crud_node
		if not data and data_node:
			data = data_node
		if not data and use_event_if_none:
			data = self.event
		if not data and error_on_empty:
			raise ExceptionParamsError("'data' not found in event root neither in 'crud' node")
		return data
	
	def get_filters(self, error_on_empty=True):
		""" get filters node from root or crud node """
		http_method = self.event.get('method', None)
		crud_node = self.event.get("crud", None)
		filter_node = self.event.get("filters", None)
		filters = None
		if http_method:
			if http_method == 'GET':
				filters = self.event.get('query', None)
			elif http_method == 'POST':
				filters = self.event.get('body', None)
		if not filters and crud_node:
			filters = crud_node
		if not filters and filter_node:
			filters = filter_node
		if not filters and error_on_empty:
			raise ExceptionParamsError("'filters' not found in event root neither in 'crud' node")
		_errors = FilterScheme().validate(data=filters)
		if _errors:
			raise Exception("Serializer validation error: {}".format(_errors))
		
		# Filter only required parameters
		if filters:
			return { f:filters[f] for f in FILTER_FIELDS if f in filters }
		else:
			return filters

class ServerlessCrudGet(ServerlessCrudBase):

	def response(self):
		""" We get a element from DB using a primary_key
		
		Parameters:
			1. "primary_keys": it can be inside a "crud" (first search)
			2. "primary_keys": It can be in the event root (second search)
			3. "primary_keys": If 1 and 2 fail, we use the whole received event (json) has primary_keys object
		
		Returns:
			[json] -- Found element of exception
		"""

		try:
			primary_keys = self.get_primary_keys()
			data = self.controller.get(primary_keys=primary_keys)
			return http_response(data=data) if self.json_response else json_decimal_to_float(data=data)
		except ExceptionParamsError as e:
			if self.json_response:
				return http_error(message="primary_keys not found in the event", detail="primary_keys is a dict", e=e)
			else:
				raise e
		except ExceptionInvalidDynamoControllerNotFound as e:
			if self.json_response:
				return http_error(message="Element not found", detail="Not found")
			else:
				raise e
		except Exception as e:
			if self.json_response:
				return http_error(message="Not expected error", detail=str(e))
			else:
				raise e


class ServerlessCrudCreate(ServerlessCrudBase):
	serializer = None

	def __init__(self, event, context, table_name, serializer=None, debug=False):
		self.serializer = serializer if not self.serializer else self.serializer
		self.verify_serializer_defined()
		return super(ServerlessCrudCreate, self).__init__(event=event, context=context, table_name=table_name, debug=debug)

	def response(self):
		try:
			data = self.get_data(use_event_if_none=True)
			self.verify_data_serialized(data=data)
			if self.auto_add_id:
				data["id"] = unique_id()
			data["ts_updated"] = current_ts()
			data_res = self.controller.create(data=data)
			return http_response(data=data_res) if self.json_response else json_decimal_to_float(data=data)
		except ExceptionInvalidDynamoControllerNotFound as e:
			if self.json_response:
				return http_error(message="Element not found", detail="Not found")
			else:
				raise e
		except Exception as e:
			if self.json_response:
				return http_error(message="Not expected error", detail=str(e))
			else:
				raise e

class ServerlessCrudUpdate(ServerlessCrudBase):
	serializer = None

	def __init__(self, event, context, table_name, serializer=None, debug=False):
		self.serializer = serializer if not self.serializer else self.serializer
		self.verify_serializer_defined()
		return super(ServerlessCrudUpdate, self).__init__(event=event, context=context, table_name=table_name, debug=debug)

	def response(self):
		try:
			primary_keys = self.get_primary_keys(use_event_if_none=False, error_on_empty=True)
			data = self.get_data(use_event_if_none=False, error_on_empty=True)
			self.verify_data_serialized(data=data, partial=True)
			data["ts_updated"] = current_ts()
			data_res = self.controller.update(primary_keys=primary_keys, data=data)
			return http_response(data=data_res) if self.json_response else json_decimal_to_float(data=data_res)
		except ExceptionInvalidDynamoControllerNotFound as e:
			if self.json_response:
				return http_error(message="Element not found", detail="Not found")
			else:
				raise e
		except Exception as e:
			if self.json_response:
				return http_error(message="Not expected error", detail=str(e))
			else:
				raise e

class ServerlessCrudDelete(ServerlessCrudBase):
	
	def response(self):
		try:
			primary_keys = self.get_primary_keys()
			data = self.controller.delete(primary_keys=primary_keys)
			return http_response(data=data) if self.json_response else json_decimal_to_float(data=data)
		except ExceptionParamsError as e:
			if self.json_response:
				return http_error(message="primary_keys not found in the event", detail="primary_keys is a dict", e=e)
			else:
				raise e
		except ExceptionInvalidDynamoControllerNotFound as e:
			if self.json_response:
				return http_error(message="Element not found", detail="Not found")
			else:
				raise e
		except Exception as e:
			if self.json_response:
				return http_error(message="Not expected error", detail=str(e))
			else:
				raise e

class ServerlessCrudFilter(ServerlessCrudBase):
	
	def response(self):
		try:
			filters = self.get_filters()
			filtered_data, count, next = self.controller.filter(**filters)
			# TODO: create next_url based on limit and next
			return http_response(data=filtered_data) if self.json_response else json_decimal_to_float(data=filtered_data)
		except Exception as e:
			if self.json_response:
				return http_error(message="Not expected error", detail=str(e))
			else:
				raise e

