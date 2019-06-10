# encoding: utf-8

import pytest

from web.dispatch.resource import ResourceDispatch


class TestResourceDispatchExtras(object):
	def test_repr(self):
		assert repr(ResourceDispatch()).startswith('ResourceDispatch(0x')
	
	def test_head_calls_get(self):
		class Foo(object):
			def get(self):
				raise NotImplementedError()
		
		disp = ResourceDispatch()
		
		with pytest.raises(NotImplementedError):
			disp.head(Foo())
	
	def test_head_returns_none(self):
		class Foo(object):
			def get(self):
				return 27
		
		disp = ResourceDispatch()
		
		assert disp.head(Foo()) is None
	
	def test_options_behaviour(self):
		disp = ResourceDispatch()
		
		assert disp.options(None) is None

