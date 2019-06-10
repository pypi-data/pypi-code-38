from inspect import isclass, isbuiltin, isroutine, getmembers, signature

from ..core import Crumb, nodefault, ipeek, prepare_path, opts

if __debug__:
	log = __import__('logging').getLogger(__name__)


class ObjectDispatch:
	"""Dispatch simulating the use of classes as collections, and attributes as resources.
	
	Underscore-prefixed attribute names are protected by default, though these protections can be explicitly disabled.
	
	
	"""
	
	__slots__ = ['protect']
	
	def __init__(self, protect=True):
		self.protect = protect
		
		if __debug__:
			log.debug("Object dispatcher prepared.", extra=dict(dispatcher=repr(self)))
		
		super(ObjectDispatch, self).__init__()
	
	def __repr__(self):
		return "ObjectDispatch(0x{id}, protect={self.protect!r})".format(id=id(self), self=self)
	
	def trace(self, context, obj):
		"""Enumerate the children of the given object, as would be accessible through dispatch."""
		
		if isroutine(obj):
			yield Crumb(self, obj, endpoint=True, handler=obj, options=opts(obj))
			return
		
		for name, attr in getmembers(obj):
			if name == '__getattr__':
				sig = signature(attr)
				path = '{' + list(sig.parameters.keys())[1] + '}'
				reta = sig.return_annotation
				
				if reta is not sig.empty:
					if callable(reta) and not isclass(reta):
						yield Crumb(self, obj, path, endpoint=True, handler=reta, options=opts(reta))
					else:
						yield Crumb(self, obj, path, handler=reta)
				
				else:
					yield Crumb(self, obj, path, handler=attr)
				
				del sig, path, reta
				continue
			
			elif name == '__call__':
				yield Crumb(self, obj, None, endpoint=True, handler=obj)
				continue
			
			if self.protect and name[0] == '_':
				continue
			
			yield Crumb(self, obj, name,
					endpoint=callable(attr) and not isclass(attr), handler=attr, options=opts(attr))
	
	def __call__(self, context, obj, path):
		protect = self.protect
		origin = obj
		current = None
		
		if __debug__:
			LE = {'dispatcher': repr(self), 'context': getattr(context, 'id', id(context))}
			log.debug("Preparing object dispatch.", extra=dict(LE, obj=obj, path=path))
		
		path = prepare_path(path)
		
		for previous, current in ipeek(path):  # Things can get hairy, so we need to track both this and the previous.
			if isclass(obj):  # We instantate classes we encounter during dispatch.
				obj = obj() if context is None else obj(context)
				
				if __debug__:
					log.debug("Instantiated class during descent.", extra=dict(LE, obj=obj))
				
				# yield Crumb(self, origin, handler=obj)
			
			if protect:
				if current[0] == '_' or isbuiltin(obj):
					if __debug__:
						log.debug("Attempt made to access a protected attribute: " + current, extra=dict(LE,
								handler = obj,
								current = current,
							))
					break  # Not being popped, this value will remain in the path.
			
			new = getattr(obj, current, nodefault)  # Attempt to get this attribute. Triggers __getattr__.
			
			if new is nodefault:  # We failed to find this attribute.
				break  # The current part, like with protected attributes, will be preserved in the path.
			
			if __debug__:
				log.debug("Retrieved attribute: " + current, extra=dict(LE, obj=new))
			
			# Commit the previously walked step.
			yield Crumb(self, origin, path=previous, handler=obj)
			
			obj = new  # Continue processing the next level of path from this point.
		
		else:  # No path left to consume. Wherever we go, there we are. This handles the "empty path" case.
			if isclass(obj):  # We instantate classes we encounter during dispatch.
				obj = obj() if context is None else obj(context)
				
				if __debug__:
					log.debug("Instantiated class at path terminus.", extra=dict(LE, obj=obj))
			
			if __debug__:
				log.debug("Dispatch complete due to exhausted path.", extra=dict(LE, obj=obj))
			
			yield Crumb(self, origin, path=current, endpoint=True, handler=obj)
			return
		
		# We bailed, so "obj" represents the last found attribute, "previous" is the path element matching that
		# object, and "current" represents the failed element. Because we bailed, "current" remains in the path.
		
		if __debug__:
			log.debug("Dispatch interrupted attempting to resolve attribute: " + current, extra=dict(LE,
					handler = repr(obj),
					endpoint = callable(obj),
					previous = previous,
					attribute = current,
				))
		
		if callable(obj):  # We don't reeeeeally care what type of callable, here...
			yield Crumb(self, origin, path=previous, endpoint=True, handler=obj, options=opts(obj))
		else:
			yield Crumb(self, origin, path=previous, endpoint=False, handler=obj, options=opts(obj))
