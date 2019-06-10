"""Database connection handling extension."""

from weakref import proxy
from functools import partial

from ..core.context import ContextGroup


class DatabaseExtension:
	_provides = {'db'}
	
	def __init__(self, default=None, **engines):
		"""Configure the database management extension."""
		
		if default is not None:
			engines['default'] = default
		
		self.engines = engines
		
		self.uses = set()
		self.needs = set()
		self.provides = set(self._provides)
		
		for name, engine in engines.items():
			if not getattr(engine, 'alias', None):
				engine.alias = name  # Inform the engine what its name is.
			
			# Update our own uses, needs, and provides flags with those provided by our hosted plugins.
			self.uses.update(getattr(engine, 'uses', ()))
			self.needs.update(getattr(engine, 'needs', ()))
			self.provides.update(getattr(engine, 'provides', ()))
		
		super().__init__()
	
	def start(self, context):
		# Construct the primary ContextGroup containing our engines.
		context.db = ContextGroup(**self.engines)
		
		# Notify our extensions of this event.
		self._handle_event('start', context)
	
	def prepare(self, context):
		# Populate the RequestContext with our set of databases bound to the context.
		context.db = context.db._promote('Databases')
		context.db['_ctx'] = proxy(context)
		
		# Notify our extensions of this event.
		self._handle_event('prepare', context)
	
	def _handle_event(self, event, *args, **kw):
		"""Broadcast an event to the database connections registered."""
		
		for engine in self.engines.values():
			if hasattr(engine, event):
				getattr(engine, event)(*args, **kw)
	
	def __getattr__(self, name):
		"""Allow the passing through of the events we don't otherwise trap to our database connection providers."""
		
		if name.startswith('_'):  # Deny access to private attributes.
			raise AttributeError()
		
		# Return a lazily bound version of the event handler
		for engine in self.engines.values():
			if name in dir(engine):
				return partial(self._handle_event, name)
		
		raise AttributeError()


class DBExtension(DatabaseExtension):
	def __init__(self, *args, **kw):
		super().__init__(*args, **kw)
		
		from warnings import warn
		warn('DBExtension is deprecated, use DatabaseExtension instead.', DeprecationWarning)
