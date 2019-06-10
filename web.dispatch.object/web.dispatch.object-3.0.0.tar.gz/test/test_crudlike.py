from collections import deque
from web.dispatch.object import ObjectDispatch

from crudlike import Person, People, Root


dispatch = ObjectDispatch()


class TestCrudlikeRoot(object):
	def test_resolve_root(self):
		result = list(dispatch(None, Root, ''))
		assert len(result) == 1
		assert result[0].endpoint  # Explicit endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
	
	def test_no_resolve_other(self):
		result = list(dispatch(None, Root, '/foo'))
		assert len(result) == 1
		assert not result[0].endpoint  # Endpoint not reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.


class TestCrudlikeCollection(object):
	def test_resolve_user_collection(self):
		result = list(dispatch(None, Root, deque(['user'])))
		assert len(result) == 2
		assert result[1].endpoint == True  # Endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
		assert isinstance(result[1].handler, People)  # Endpoint is People instance.
		assert result[1].handler() == "I'm all people."
	
	def test_resolve_specific_user(self):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice'])))
		assert len(result) == 3
		assert result[2].endpoint == True  # Endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
		assert isinstance(result[1].handler, People)  # Intermediate is People instance.
		assert isinstance(result[2].handler, Person)  # Endpoint is Person instance.
		assert result[2].handler() == "Hi, I'm GothAlice"
	
	def test_resolve_specific_user_action(self):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice', 'foo'])))
		assert len(result) == 4
		assert result[3].endpoint == True  # Endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
		assert isinstance(result[1].handler, People)  # Intermediate is People instance.
		assert isinstance(result[2].handler, Person)  # Endpoint is Person instance.
		assert result[3].handler() == "I'm also GothAlice"


class TestCrudlikeTraces(object):
	def test_root_shallow(self):
		trace = list(dispatch.trace(None, Root))
		
		assert len(trace) == 1  # Only one accessible child object.
		assert str(trace[0].path) == 'user'
		assert trace[0].endpoint == False  # A shallow search can't tell that this is a valid endpoint.
	
	def test_root_instance_shallow(self):
		trace = list(dispatch.trace(None, Root()))
		
		assert len(trace) == 1  # Only one accessible child object.
		assert str(trace[0].path) == 'user'
		assert trace[0].endpoint == False  # A shallow search can't tell that this is a valid endpoint.
	
	def test_people_shallow(self):
		trace = list(dispatch.trace(None, People))
		
		assert len(trace) == 2  # Only one accessible child object.
		assert trace[0].path is None
		assert trace[0].endpoint == True
		assert trace[0].handler is People
		
		assert str(trace[1].path) == '{username}'
		assert trace[1].endpoint == False
		assert trace[1].handler is Person
	
	def test_people_instance_shallow(self):
		inst = People()
		trace = list(dispatch.trace(None, inst))
		
		assert len(trace) == 2  # Only one accessible child object.
		assert trace[0].path is None
		assert trace[0].endpoint == True
		assert trace[0].handler is inst
		
		assert str(trace[1].path) == '{username}'
		assert trace[1].endpoint == False
		assert trace[1].handler is Person
	
	def test_person_shallow(self):
		trace = list(dispatch.trace(None, Person))
		
		assert len(trace) == 2  # Only one accessible child object.
		assert trace[0].path is None
		assert trace[0].endpoint == True
		assert trace[0].handler is Person
		
		assert str(trace[1].path) == 'foo'
		assert trace[1].endpoint == True
		assert trace[1].handler is Person.foo
	
	def test_person_instance_shallow(self):
		inst = Person('GothAlice')
		trace = list(dispatch.trace(None, inst))
		
		assert len(trace) == 2  # Only one accessible child object.
		assert trace[0].path is None
		assert trace[0].endpoint == True
		assert trace[0].handler is inst
		
		assert str(trace[1].path) == 'foo'
		assert trace[1].endpoint == True
		assert trace[1].handler is Person.foo  # Should this be inst.foo?
