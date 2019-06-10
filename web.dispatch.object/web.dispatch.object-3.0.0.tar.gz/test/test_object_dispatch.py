# encoding: utf-8

from __future__ import unicode_literals

from web.dispatch.core import nodefault
from web.dispatch.object import ObjectDispatch

from sample import path, function, Simple, ClassDynamicAttribute, FunctionDynamicAttribute, CallableShallow, \
		CallableDeep, CallableMixed, AnonymousDynamicAttribute


# We pre-create these for the sake of convienence.
# In ordinary usage frameworks should try to avoid excessive reinstantiation where possible.
dispatch = ObjectDispatch()
promiscuous = ObjectDispatch(protect=False)



def test_nodefault_repr():
	assert repr(nodefault) == "<no default>"



class TestDispatchPathCasting:
	def test_string_value(self):
		result = list(dispatch(None, function, '/'))
		
		assert len(result) == 1
	
	def test_list_value(self):
		result = list(dispatch(None, function, ['foo', 'bar']))
		
		assert len(result) == 1


class TestFunctionDispatch:
	def test_root_path_resolves_to_function(self):
		result = list(dispatch(None, function, path('/')))
		assert len(result) == 1
		assert result[0].path == None
		assert result[0].handler == function
		assert result[0].endpoint == True
		
	def test_deep_path_resolves_to_function(self):
		result = list(dispatch(None, function, path('/foo/bar/baz')))
		assert len(result) == 1
		assert result[0].path == None
		assert result[0].handler == function
		assert result[0].endpoint == True
	
	def test_trace_early_exit(self):
		result = list(dispatch.trace(None, function))
		assert len(result) == 1
		
		result = result[0]
		assert result.endpoint
		assert result.handler is function
		assert result.options == {'GET', 'POST'}


class TestDynamicAttribute:
	def test_dynamic_anonymous(self):
		result = list(dispatch.trace(None, AnonymousDynamicAttribute))
		assert len(result) == 1
		
		result = result[0]
		assert not result.endpoint
		assert str(result.path) == '{name}'
		assert result.handler is AnonymousDynamicAttribute.__getattr__
		assert result.options is None
		
	def test_dynamic_class(self):
		result = list(dispatch.trace(None, FunctionDynamicAttribute))
		assert len(result) == 1
		
		result = result[0]
		assert result.endpoint
		assert str(result.path) == '{name}'
		assert result.handler is function
		assert result.options == {'GET', 'POST'}
	
	def test_dynamic_function(self):
		result = list(dispatch.trace(None, ClassDynamicAttribute))
		assert len(result) == 1
		
		result = result[0]
		assert not result.endpoint
		assert str(result.path) == '{name}'
		assert result.handler is Simple
		assert result.options is None


class TestSimpleDispatch:
	def test_protected_init_method(self):
		result = list(dispatch(None, Simple, path('/__init__')))
		assert len(result) == 1
		
		assert result[0].path == None
		assert isinstance(result[0].handler, Simple)
		assert result[0].endpoint == False
	
	def test_protected_simple_value(self):
		result = list(dispatch(None, Simple, path('/_protected')))
		assert len(result) == 1
		
		assert result[0].path == None
		assert isinstance(result[0].handler, Simple)
		assert result[0].endpoint == False
	
	def test_static_attribute(self):
		result = list(dispatch(None, Simple, path('/static')))
		assert len(result) == 2
		
		assert result[0].path == None
		assert isinstance(result[0].handler, Simple)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == 'static'
		assert result[1].handler == "foo"
		assert result[1].endpoint == True
	
	def test_shallow_class_lookup(self):
		result = list(dispatch(None, Simple, path('/foo')))
		assert len(result) == 2
		
		assert result[0].path == None
		assert isinstance(result[0].handler, Simple)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, Simple.foo)
		assert result[1].endpoint == True
	
	def test_deep_class_lookup(self):
		result = list(dispatch(None, Simple, path('/foo/bar')))
		assert len(result) == 3
		
		assert result[0].path == None
		assert isinstance(result[0].handler, Simple)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, Simple.foo)
		assert result[1].endpoint == False
		
		assert str(result[2].path) == "bar"
		assert isinstance(result[2].handler, Simple.foo.bar)
		assert result[2].endpoint == True
	
	def test_partial_incomplete_lookup(self):
		result = list(dispatch(None, Simple, path('/foo/bar/diz')))
		assert len(result) == 3
		
		assert result[0].path == None
		assert isinstance(result[0].handler, Simple)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, Simple.foo)
		assert result[1].endpoint == False
		
		assert str(result[2].path) == "bar"
		assert isinstance(result[2].handler, Simple.foo.bar)
		assert result[2].endpoint == False
	
	def test_deepest_endpoint_lookup(self):
		result = list(dispatch(None, Simple, path('/foo/bar/baz')))
		assert len(result) == 4
		
		assert result[0].path == None
		assert isinstance(result[0].handler, Simple)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, Simple.foo)
		assert result[1].endpoint == False
		
		assert str(result[2].path) == "bar"
		assert isinstance(result[2].handler, Simple.foo.bar)
		assert result[2].endpoint == False
		
		assert str(result[3].path) == "baz"
		assert result[3].handler() == "baz"
		assert result[3].endpoint == True


class TestCallableShallowDispatch:
	def test_root_path_resolves_to_instance(self):
		result = list(dispatch(None, CallableShallow, path('/')))
		assert len(result) == 1
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableShallow)
		assert result[0].endpoint == True
		
	def test_deep_path_resolves_to_instance(self):
		result = list(dispatch(None, CallableShallow, path('/foo/bar/baz')))
		assert len(result) == 1
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableShallow)
		assert result[0].endpoint == True


class TestCallableDeepDispatch:
	'''
	class CallableDeep:
	__init__ = init
	
	class foo:
		__init__ = init
		
		class bar:
			__init__ = init
			
			def __call__(self, method):
				return method
	
	'''
	def test_shallow_class_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo')))
		assert len(result) == 2
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableDeep)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableDeep.foo)
		assert result[1].endpoint == True
	
	def test_deep_callable_class_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo/bar')))
		assert len(result) == 3
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableDeep)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableDeep.foo)
		assert result[1].endpoint == False
		
		assert str(result[2].path) == "bar"
		assert isinstance(result[2].handler, CallableDeep.foo.bar)
		assert result[2].endpoint == True
	
	def test_incomplete_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo/diz')))
		assert len(result) == 2
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableDeep)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableDeep.foo)
		assert result[1].endpoint == False
	
	def test_beyond_callable_class_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo/bar/baz')))
		assert len(result) == 3
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableDeep)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableDeep.foo)
		assert result[1].endpoint == False
		
		assert str(result[2].path) == "bar"
		assert isinstance(result[2].handler, CallableDeep.foo.bar)
		assert result[2].endpoint == True


class TestCallableMixedDispatch:
	'''
	class CallableMixed:
	__init__ = init
	
	def __call__(self, *args):
		return '/' + '/'.join(args)
	
	class foo:
		__init__ = init
		
		class bar:
			__init__ = init
			
			def baz(self):
				return "baz"
	'''
	def test_shallow_class_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo')))
		assert len(result) == 2
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableMixed)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableMixed.foo)
		assert result[1].endpoint == True
	
	def test_deep_callable_class_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo/bar')))
		assert len(result) == 3
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableMixed)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableMixed.foo)
		assert result[1].endpoint == False
		
		assert str(result[2].path) == "bar"
		assert isinstance(result[2].handler, CallableMixed.foo.bar)
		assert result[2].endpoint == True
	
	def test_incomplete_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo/diz')))
		assert len(result) == 2
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableMixed)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableMixed.foo)
		assert result[1].endpoint == False
	
	def test_deepest_endpoint_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo/bar/baz')))
		assert len(result) == 4
		
		assert result[0].path == None
		assert isinstance(result[0].handler, CallableMixed)
		assert result[0].endpoint == False
		
		assert str(result[1].path) == "foo"
		assert isinstance(result[1].handler, CallableMixed.foo)
		assert result[1].endpoint == False
		
		assert str(result[2].path) == "bar"
		assert isinstance(result[2].handler, CallableMixed.foo.bar)
		assert result[2].endpoint == False
		
		assert str(result[3].path) == "baz"
		assert result[3].handler() == 'baz'
		assert result[3].endpoint == True
