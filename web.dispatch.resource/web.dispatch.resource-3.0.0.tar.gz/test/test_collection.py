# encoding: utf-8

import pytest

from web.dispatch.resource.helper import Collection, Resource

from helper import Rig


class TestCollection(Rig):
	class root(Collection):
		class __resource__(Resource):
			def get(self):
				return "I am " + self._record
			
			def post(self):
				return self._collection.__class__.__name__ + " updated"
		
		def get(self):
			return "all things"
		
		def __getitem__(self, item):
			if item == "Eve":
				raise KeyError()
			
			return item
	
	def test_dispatcher(self):
		assert Collection.__dispatch__ == 'resource'
	
	def test_resource(self):
		assert Collection.__resource__ is None
	
	def test_getitem_failure(self):
		coll = Collection(None)
		
		with pytest.raises(NotImplementedError):
			coll[27]
	
	def test_top_level_operations(self):
		assert self.do('get').text == "all things"
	
	def test_lookup_get(self):
		assert self.do('get', '/Bob').text == "I am Bob"
	
	def test_lookup_post(self):
		assert self.do('post', '/Alice').text == "root updated"
	
	def test_invalid_lookup(self):
		assert self.do('get', '/Eve').status_int == 404
		assert self.do('delete', '/Eve').status_int == 404

