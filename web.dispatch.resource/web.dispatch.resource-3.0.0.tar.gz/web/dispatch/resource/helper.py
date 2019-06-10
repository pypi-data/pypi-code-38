"""Helpers for advanced controller behaviour.

Much work needs to be done.
"""

from functools import partial, wraps


class Resource:
	__dispatch__ = 'resource'
	
	def __init__(self, context, collection=None, record=None):
		self._ctx = context
		self._collection = collection
		self._record = record


class Collection(Resource):
	__resource__ = None
	
	def __getitem__(self, identifier):
		raise NotImplementedError()
