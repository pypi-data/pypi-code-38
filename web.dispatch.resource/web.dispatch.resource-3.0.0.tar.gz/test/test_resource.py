# encoding: utf-8

from web.dispatch.resource.helper import Resource

from helper import Rig


class TestResource(object):
	def test_dispatcher(self):
		assert Resource.__dispatch__ == 'resource'
	
	def test_constructor(self):
		res = Resource(1, 2, 3)
		assert res._ctx is 1
		assert res._collection is 2
		assert res._record is 3
	
	def test_constructor_defaults(self):
		res = Resource(1)
		assert res._ctx is 1
		assert res._collection is res._record is None


class TestResourceRuntime(Rig):
	class root(Resource):
		def get(self):
			return "get"
		
		def post(self):
			return "post"
		
		def put(self):
			return "put"
		
		def delete(self):
			return "delete"
		
		def custom(self):
			return "custom"
		
		class other(Resource):
			def get(self):
				return "got"
			
			def post(self):
				return "did"
	
	def test_basic_verbs(self):
		assert self.do('get').text == "get"
		assert self.do('post').text == "post"
		assert self.do('put').text == "put"
		assert self.do('delete').text == "delete"
		assert self.do('custom').text == "custom"
	
	def test_verb_replacement(self):
		assert self.do('get', '/delete').text == "delete"
		assert self.do('get', '/head').text == ""
	
	def test_other_descent(self):
		assert self.do('get', '/other').text == "got"
		assert self.do('post', '/other').text == "did"
	
	def test_invalid(self):
		assert self.do('invalid').status_int == 405
	
	def test_head(self):
		assert self.do('head').text == ""
	
	def test_allow(self):
		verbs = set(self.do('get').headers['Allow'].split(', '))
		assert {'GET', 'POST', 'PUT', 'DELETE', 'CUSTOM', 'HEAD', 'OPTIONS'}.issubset(verbs)
	
	def test_options(self):
		verbs = set(self.do('get').headers['Allow'].split(', '))
		assert {'GET', 'POST', 'PUT', 'DELETE', 'CUSTOM', 'HEAD', 'OPTIONS'}.issubset(verbs)

