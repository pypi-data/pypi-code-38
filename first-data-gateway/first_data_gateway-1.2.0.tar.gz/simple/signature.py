import uuid
import time
import hmac
import hashlib
import base64
import json
import six
import datetime

class Signature:
	
	PRIMITIVE_TYPES = (float, bool, bytes, six.text_type) + six.integer_types

	def __init__(self, params):
		self.api_key = params['api_key']
		self.api_secret = params['api_secret']
		self.client_request_id = str(uuid.uuid4())
		self.timestamp = str(int(round(time.time()*1000)))

	def sign(self, payload=None):
		data = self.api_key + self.client_request_id + self.timestamp
		if payload:
			data += json.dumps(self.sanitize_for_serialization(payload))
		h = hmac.new(self.api_secret, data, hashlib.sha256).hexdigest()
		return base64.b64encode(h)

	def sanitize_for_serialization(self, obj):
		if obj is None:
			return None
		elif isinstance(obj, self.PRIMITIVE_TYPES):
			return obj
		elif isinstance(obj, list):
			return [self.sanitize_for_serialization(sub_obj)
				for sub_obj in obj]
		elif isinstance(obj, tuple):
			return tuple(self.sanitize_for_serialization(sub_obj)
				for sub_obj in obj)
		elif isinstance(obj, (datetime.datetime, datetime.date)):
			return obj.isoformat()

		if isinstance(obj, dict):
			obj_dict = obj
		else:
			obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
				for attr, _ in six.iteritems(obj.openapi_types)
				if getattr(obj, attr) is not None}

		return {key: self.sanitize_for_serialization(val)
				for key, val in six.iteritems(obj_dict)}