# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (c) 2017-2019 Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$
__all__ = [
	'ClassWithManagedProperties',
	'ManagedProperty',
	'ManagedShortcut',
	
	'WrapEachParagraph', # TODO: would like to remove, but needed for pydoc
]

import os
import re
import sys
import math
import inspect
import weakref
import textwrap

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )


SPHINXDOC = any( os.environ.get( varName, '' ).lower() not in [ '', '0', 'false' ] for varName in [ 'SPHINX' ] )
DRYDOC = SPHINXDOC

numpy = None
try: import numpy
except: pass

PROPS_TMP = []
SHORTCUTS_TMP = []

# non-numpy alternatives for `seq.size` and `seq.flat = values`, used only if `seq` is not a numpy array (which will in turn only happen if numpy was not successfully imported):
def numel( seq ):
	try: return seq.size
	except: return len( seq )
def assign_sequence( seq, values ):
	"""
	Fallback for creating behaviour like `seq.flat = values` when `numpy` is not
	available.
	"""
	try: len( values )
	except: values = [ values ]
	else:
		try: values.flat # unlikely that values has it when seq doesn't,  but let's handle that case just for completeness
		except: pass
		else: values = list( values.flat )
	nNeeded = len( seq )
	nSupplied = len( values )
	if nSupplied < nNeeded:
		values = list( values ) * int( math.ceil( nNeeded / float( nSupplied ) ) )
	seq[ : ] = values[ :nNeeded ]


class ClassWithManagedProperties( object ):
	"""
	Useful base class for any class to which you intend to attach `ManagedProperty`
	or `ManagedShortcut` descriptors.
	
	Use `@ClassWithManagedProperties._Organize` as a class decorator when you define
	a subclass.
	"""
	
	_RecordChange = None
	_dynamics = None
			
	@staticmethod
	def _Organize( cls ):
		"""
		Use `@ClassWithManagedProperties._Organize` as a decorator on the
		class declaration for any `ClassWithManagedProperties` subclass.
		"""
		fieldname = '_managed_properties' # do not inflect this with cls.__name__ if you want a complete list including inherited properties
		props = list( getattr( cls, fieldname, [] ) ) # make a shallow copy of any list this class may have inherited
		setattr( cls, fieldname, props )
		props.extend( PROPS_TMP )
		PROPS_TMP[ : ] = []
		fieldname = '_managed_shortcuts' # do not inflect this with cls.__name__ if you want a complete list including inherited properties
		shortcuts = list( getattr( cls, fieldname, [] ) ) # make a shallow copy of any list this class may have inherited
		setattr( cls, fieldname, shortcuts )
		shortcuts.extend( SHORTCUTS_TMP )
		SHORTCUTS_TMP[ : ] = []
		names = dir( cls )
		for name in names:
			obj = getattr( cls, name )
			if   isinstance( obj, ManagedProperty ): obj.order = 0.0 + obj.order_defined / ( len( props ) * 10.0 )
			elif isinstance( obj, ManagedShortcut ): obj.order = 1.0 + obj.order_defined / ( len( shortcuts ) * 10.0 )
			else: continue
			obj.owner = cls.__name__
			if name.endswith( '_' ):
				delattr( cls, name )
				name = name.rstrip( '_' )
				setattr( cls, name, obj )
				obj.name = name # trailing underscores are removed but they denote the canonical name
			elif name not in obj.names:
				obj.names.append( name )
				
		#for obj in props + shortcuts: print( obj )
		if DRYDOC:
			for p in cls.Properties( True ):
				if isinstance( p, ManagedShortcut ) and not p.parent.__doc__: setattr( cls, p.name, SimpleDocWrapper( None ) ); continue
				if not p.__doc__: continue
				for name in p.names[ 1: ]: setattr( cls, name, SimpleDocWrapper( '`.%s` is an alias for `.%s`' % ( name, p.names[ 0 ] ) ) )
		return cls
	
	@classmethod
	def _AddCustomProperty( cls, managedItemDescriptor, index=None ):
		if isinstance( managedItemDescriptor, ManagedShortcut ):
			fieldname = '_managed_shortcuts'
		elif isinstance( managedItemDescriptor, ManagedProperty ):
			fieldname = '_managed_properties'
		else:
			raise TypeError( 'do not know how to add items of type %r' % type( managedItemDescriptor ) )
		for name in managedItemDescriptor.names:
			previous = getattr( cls, name, None )
			if previous and not getattr( previous, 'custom', False ):
				raise AttributeError( 'duplicate name %r: the %s class already an attribute of this name' % ( name, cls.__name__ ) )
		name = managedItemDescriptor.name
		if not name: raise ValueError( 'cannot add unnamed items' )
		registry = list( getattr( cls, fieldname, [] ) )
		setattr( cls, fieldname, registry )
		if index is None: index = len( registry )
		predecessor_order = registry[ -1 ].order
		managedItemDescriptor.order = 0.5 * ( predecessor_order + math.ceil( predecessor_order ) )
		registry.insert( index, managedItemDescriptor )
		for name in managedItemDescriptor.names:
			setattr( cls, name, managedItemDescriptor )
		managedItemDescriptor.custom = True
		return managedItemDescriptor
			
		
	def _RunDynamics( self, t ):
		dynamics = getattr( self, '_dynamics', None )
		if dynamics is None: dynamics = self._dynamics = {}
		updates = {}
		for order, name, func in sorted( dynamics.values() ):
			try:
				value = func( t )
			except StopIteration as exc:
				value = None
				for arg in exc.args:
					if isinstance( arg, dict ):
						if value is None: value = arg.pop( '_', None )
						updates.update( arg )
					else: value = arg
				dynamics.pop( name )
				if value is not None: setattr( self, name, value )
			except:
				einfo = sys.exc_info()
				sys.stderr.write( 'Exception while evaluating dynamic .%s property of %s:\n' % ( name, self ) )
				getattr( self, '_excepthook', sys.excepthook )( *einfo )
				dynamics.pop( name )
			else:
				if value is not None: setattr( self, name, value )
				dynamics[ name ] = ( order, name, func )
				
		for name, value in updates.items():
			setattr( self, name, value )

	def SetDynamic( self, name, func, order=-1, canonicalized=False ):
		"""
		Associate a "dynamic" (i.e. a function that can be called repeatedly
		to set an attribute) with the name of an attribute.
		
		For example::
		
			foo.Set( 'bar',  lambda t: t ** 2 )
		
		This will set `foo.bar` to `t ** 2`  every time the method
		`foo._RunDynamics( t )` is called (this call will happen automatically
		from the API user's point of view, in the object's infrastructure
		implementation).
		
		A dynamic can be attached to any attribute name. If the `.bar` attribute
		happens to be a `ManagedProperty` or `ManagedShortcut`, then it will
		also automatically support "dynamic value assignment", i.e. you can do::
		
			foo.bar = lambda t: t ** 2
			
		as a syntactic shorthand for `.SetDynamic()`---the setter will detect
		the fact that the value is callable, and divert it to the register of
		dynamics rather than assigning it directly (so the actual static value
		you get from querying `foo.bar` will not immediately change).
		
		Args:
			name (str)
				name of the attribute
			func
				callable object, or `None` to remove any dynamic that may
				already be associated with `name`
			order (int, float)
				optional numeric ordering key that allows you to control the
				serial order in which dynamics are evaluated
			canonicalized (bool)
				for internal use only.  `ManagedProperty` and `ManagedShortcut`
				descriptors can have multiple aliases. The default settings,
				`canonicalized=False` says that `name` hsa not necessarily been
				translated to the descriptor's canonical name, so this should be
				attempted
		
		Returns:
			self
			
		See also:  `.GetDynamic()`, `.GetDynamics()`, `.ClearDynamics()`
		"""
		dynamics = getattr( self, '_dynamics', None )
		if not canonicalized:
			try:
				name = self.GetPropertyDescriptor( name ).names[ 0 ]
			except:
				if not hasattr( self, name ):
					setattr( self, name, None )
		if func:
			if dynamics is None: dynamics = self._dynamics = {}
			if inspect.isgeneratorfunction( func ): func = func()
			if inspect.isgenerator( func ): gen = func; func = lambda _: next( gen )
			dynamics[ name ] = ( order, name, func )
		else:
			if dynamics: dynamics.pop( name, None )
		return self
	
	def GetDynamic( self, name ):
		"""
		For dynamic properties, return the actual callable object that
		generates property values, rather than the current static value.

		Args:
		    name (str): Name of the property
		
		Returns:
		    Callable object responsible for generating values for the named
		    property (or `None` if there is no such dynamic).

		See also:  `.GetDynamics()`, `.SetDynamic()`, `.ClearDynamics()`
		"""
		dynamics = getattr( self, '_dynamics', None )
		if not dynamics: return None
		descriptor = getattr( self.__class__, name, None )
		name = getattr( descriptor, 'name', name )
		value = dynamics.get( name, None )
		if not value: return None
		order, name, func = value
		return func
		
	def GetDynamics( self ):
		"""
		Get an ordered list of (name, callable) tuples detailing all the
		dynamics of this instance.
		
		See also:  `.GetDynamic()`, `.SetDynamic()`, `.ClearDynamics()`

		"""
		dynamics = self._dynamics
		if dynamics: return [ ( name, func ) for order, name, func in sorted( dynamics.values() ) ]
		else: return []
		
	def ClearDynamics( self ):
		"""
		Remove all property dynamics from the instance.
		
		See also:  `.GetDynamic()`, `.GetDynamics()`, `.SetDynamic()`
		"""
		dynamics = self._dynamics
		if dynamics: dynamics.clear()
		return self

	@classmethod
	def Properties( cls, includeShortcuts=False ):
		"""
		Return a list of all managed properties of this class. (Class method)

		Args:
		    includeShortcuts:
		        Determines whether `ManagedShortcut` instances should be included (`True`) 
		        or not (`False`; default) along with `ManagedProperty` instances.
		
		Returns:
		    A list of `ManagedProperty` (and optionally also `ManagedShortcut`) descriptor
		    instances.
		"""
		props = list( cls._managed_properties )
		if includeShortcuts: props.extend( cls._managed_shortcuts )
		return props
		
	def Set( self, **kwargs ):
		"""
		Set the values of multiple managed properties in one call. An error will be raised
		if you try to set the value of a non-existent, or non-managed, property.

		Returns:
		    `self`

		Example::
		
		    instance.Set( rotation=90, color=(0, 0, 1),  contrast=0.5 )
		
		"""
		splits = {}
		delim = '_'
		for propertyName, value in kwargs.items():
			if not hasattr( self, propertyName ):
				split = propertyName.split( delim )
				if len( split ) > 1 and hasattr( self, split[ 0 ] ):
					splits.setdefault( split[ 0 ], {} )[ delim.join( split[ 1: ] ) ] = value
				else:
					raise AttributeError( '%s class does not have a %r property' % ( self.__class__.__name__, propertyName ) )
			setattr( self, propertyName, value )
		for childName, props in splits.items():
			child = getattr( self, childName )
			childMethod = getattr( child, 'Set', None )
			if not childMethod: raise AttributeError( '%s class does not have a %r property' % ( self.__class__.__name__, childName + delim + list( props.keys() )[ 0 ] ) )
			child.Set( **props )
		return self
		
	def Inherit( self, other ):
		"""
		Set the values of all managed properties of this instance to match those of another instance.
		Only properties common to both objects will be considered. Dynamic property values will be
		copied as dynamic properties.

		Args:
		    other:  instance whose property values will be copied to the properties of `self`
		
		Returns:
		    `self`
		"""
		names = [ prop.name for prop in self.Properties( False ) ]
		for name in names:
			value = getattr( other, name, None )
			if hasattr( self, name ) and value is not None: setattr( self, name, value )
		dynamics = getattr( other, '_dynamics', None )
		if dynamics:
			for name, ( order, attrName, func ) in dynamics.items():
				if hasattr( self, name ): setattr( self, name, func )
		return self
	
	@classmethod
	def SetDefault( cls, **kwargs ):
		"""
		Affects the class. Sets the default values of named properties.
		In instances of the class created subsequently, managed properties
		will have the new default values.
		
		Example::
			
			cls.SetDefault( color=(1,0,0), rotation=90 )
			
		"""
		for key, value in kwargs.items():
			desc = getattr( cls, key )
			if isinstance( desc, ( ManagedProperty, ManagedShortcut ) ): desc.SetDefault( value )
			else: raise AttributeError( '%s class has no managed property %r' % ( cls.__name__, key ) )
			
	@classmethod
	def GetPropertyDescriptor( cls, propertyName ):
		descriptor = getattr( cls, propertyName, None )
		if isinstance( descriptor, ManagedShortcut ): raise ValueError( '%r is the name of a shortcut, not a fully-fledged property - cannot link it across objects' % propertyName )
		elif not isinstance( descriptor, ManagedProperty ): raise ValueError( '%r is not a managed property of the %s class' % ( propertyName, cls.__name__ ) )
		return descriptor
		
	def _RedirectProperty( self, propertyName, targetInstance, targetArray=None ):
		if targetInstance is None: targetInstance = self  # either targetInstance=None or targetInstance=self means "go independent"
		myDescriptor = self.GetPropertyDescriptor( propertyName )
		propertyName = myDescriptor.name # canonicalize name
		if targetArray is None: # targetArray is provided for efficiency only - we can retrieve it here:
			targetArray = targetInstance.GetPropertyDescriptor( propertyName ).determine_array( targetInstance, name=propertyName )
		if targetInstance is self: targetArray = targetArray * 1
		myDescriptor.determine_array( self, name=propertyName, array=targetArray )
		
	def ShareProperties( self, *pargs, **kwargs ):
		"""
		Share the underlying array storage of the named managed properties with other objects, so that a change to
		one affects all.  Optionally, set the values at the same time. Calling syntax is flexible - the following
		examples all take certain property arrays associated with instance `a` and share them with instances `b`,
		`c` and `d`::

			a.ShareProperties( 'gamma noiseAmplitude backgroundColor', b, c, d )
			a.ShareProperties( ['gamma', 'noiseAmplitude', 'backgroundColor'], [b, c], d )
			a.ShareProperties( b, c, d,  gamma=-1, noiseAmplitude=0.01, backgroundColor=0.5 ) # sets values at the same time
		
		A similar effect can be obtained via `b.LinkPropertiesWithMaster( a, ... )`---although there you are
		limited to one sharee at a time---and a syntactic shorthand for this is to pretend you are assigning the
		master object instance itself to the target property::
		
			b.gamma = a
		
		Undo with `.MakePropertiesIndependent()`  (or `b.gamma = b`)
		
		Returns:
		    `self`
		""" # TODO: doc is Shady-specific... and should probably not be
		isseq = lambda x: hasattr( x, '__iter__' ) and not hasattr( x, 'split' )
		others = [ arg3        for arg1 in pargs for arg2 in ( arg1 if isseq( arg1 ) else [ arg1 ] ) for arg3 in ( arg2.replace( ',', ' ' ).split() if hasattr( arg2, 'split' ) else [ arg2 ] ) if not isinstance( arg3, basestring ) and arg3 is not self ]
		props  = { arg3 : None for arg1 in pargs for arg2 in ( arg1 if isseq( arg1 ) else [ arg1 ] ) for arg3 in ( arg2.replace( ',', ' ' ).split() if hasattr( arg2, 'split' ) else [ arg2 ] ) if     isinstance( arg3, basestring ) }
		props.update( kwargs )
		for key, value in props.items():
			if value is not None: setattr( self, key, value )
		for propertyName in props:
			descriptor = self.GetPropertyDescriptor( propertyName )
			propertyName = descriptor.name # canonicalize
			array = descriptor.determine_array( self, name=propertyName )
			for other in others:
				other.SetDynamic( propertyName, None, canonicalized=True )
				recordChange = other._RecordChange
				if recordChange: recordChange( other, propertyName, link=self )
				other._RedirectProperty( propertyName=propertyName, targetInstance=self, targetArray=array )
		return self
		
	def LinkPropertiesWithMaster( self, master, *pargs, **kwargs ):
		"""
		See `.ShareProperties()`
		
		Returns:
		    `self`
		"""
		if master is self: self.MakePropertiesIndependent( *pargs, **kwargs )
		else: master.ShareProperties( self, *pargs, **kwargs )
		return self
	
	def MakePropertiesIndependent( self, *pargs, **kwargs ):
		"""
		Undoes the effect of `.ShareProperties()`. Optionally, set the values of the properties after unsharing.
		
		Example::
			
			a.ShareProperties( b, c, d, alpha=1, beta=2, gamma=3 )
			b.MakePropertiesIndependent( alpha=4 )
			# Now `a` and `b` share properties `.beta` and `.gamma`, but
			# `b.alpha` is independent and already has the new value 4;
			# by contrast `a`, `c` and `d` still share all three properties.
			
			c.MakePropertiesIndependent( 'beta', 'gamma' )
			# Now `c` does not share anything except `.alpha`, although the
			# property values themselves have not yet been changed.
			
			c.Set( beta=c, gamma=c )
			# a syntactic shorthand for the same operation as in the previous
			# line
			
		Returns:
		    `self`
		"""
		isseq = lambda x: hasattr( x, '__iter__' ) and not hasattr( x, 'split' )
		props  = { arg3 : None for arg1 in pargs for arg2 in ( arg1 if isseq( arg1 ) else [ arg1 ] ) for arg3 in arg2.replace( ',', ' ' ).split() }
		props.update( kwargs )
		for propertyName, value in props.items():
			self._RedirectProperty( propertyName=propertyName, targetInstance=None )
			recordChange = self._RecordChange
			if recordChange: recordChange( self, propertyName, link=self )
			if value is not None: setattr( self, propertyName, value )
		return self	
	
class SimpleDocWrapper( object ):
	__doc__ = property( lambda self: self.__doc )
	def __init__( self, docstring ): self.__doc = docstring
	def __get__( self, instance, owner=None ): return self
	def __set__( self, instance, value ): return self

def MakeScalarWrapper( proxy_object, example_value ):
	class property_value( example_value.__class__ ): __doc__ = property( lambda self: proxy_object.__doc__ ) # bakes `proxy_object`: this enables `x.bgred?` where `x` is an instance `X` that owns this ManagedProperty instance
	return property_value

def WrapPropertyArray( value, proxy_object ):
	if not numpy:
		try: len( value )
		except: return [ value ]
		else: return value
	class property_array( numpy.ndarray ):
		__doc__ = property( lambda self: proxy_object.__doc__ ) # bakes `proxy_object`: this enables `x.backgroundColor?` where `x` is an instance of a class `X` that owns this ManagedProperty instance
		def __new__( cls, arg ): return numpy.asarray( arg ).view( cls )
	value = property_array( value )
	return value.reshape( [ value.size ] ) # unlike flatten(), this doesn't deep-copy the array data

def WrapEachParagraph( txt, **kwargs ):
	try: textwrap.wrap( '', tabsize=4 )
	except: kwargs.pop( 'tabsize', None )
	else: kwargs.setdefault( 'tabsize', 4 )
	lines = []
	txt = '\n' + txt.strip( '\n' )
	leading = re.match( r'^\s*', txt ).group()
	txt = txt.replace( leading, '\n' ).strip()
	for para in txt.replace( '\n\n', '\v' ).split( '\v' ):
		if lines: lines.append( '' )
		lines.extend( textwrap.wrap( para, **kwargs ) )
	return '\n'.join( lines )

class ManagedProperty( object ):
	def __init__( self, default, transfer=None, doc='', canonical_name=None, read_only=False, notes='', names=(), default_string='' ):
		"""
		For general information about the ManagedProperty descriptor
		class, see either:
		   * :ref:`the online documentation on managed properties and
		     shortcuts <ManagedProperties>`
		   * or: the docstring of `Shady.Documentation.ManagedPropertiesAndShortcuts`
		"""
		PROPS_TMP.append( self )
		self.order_defined = len( PROPS_TMP )
		self.shortcuts = {}
		self.default = WrapPropertyArray( default, self )
		self.scalarWrapper = MakeScalarWrapper( self, self.default[ 0 ] )
		self.transfer = transfer
		self.read_only = read_only # TODO: currently unused
		self.names = list( names )
		if canonical_name: self.name = canonical_name
		self.owner = '{cls}'
		self.doc = doc
		self.notes = notes
		self.custom = False
		self.default_string = default_string
		self.default_changed = False
		
	def __repr__( self ): # TODO: remove
		s = '<{cls} object at 0x{id:08x}>'.format( cls=self.__class__.__name__, id=id( self ) )
		if self.names: s += ': ' + '|'.join( self.names )
		return s
	def determine_array( self, instance, array=None, name=None ):
		storage = getattr( instance, '_property_storage', None )
		if storage is None: storage = instance._property_storage = {}
		if name is None: name = self.names[ 0 ]
		if array is not None: storage[ name ] = array; return array
		array = storage.get( name, None )
		if array is None: array = storage[ name ] = self.default * 1  # makes a copy of self.default regardless of whether it is a numpy array or a list
		return array
	@property
	def name( self ):
		return self.names[ 0 ] if self.names else None
	@name.setter
	def name( self, value ):
		if value in self.names: del self.names[ self.names.index( value ) ]
		if value: self.names.insert( 0, value )
	@property
	def notes( self ):
		return [ shortcut.note for index, shortcut in sorted( self.shortcuts.items() ) ]
	@notes.setter
	def notes( self, value ):
		if not value and not self.shortcuts: return
		if hasattr( value, 'split' ): value = value.split( ';' )
		for shortcut, note in zip( self, value ): shortcut.note = note.strip()
	@property
	def __doc__( self ): # ...whereas this enables `X.backgroundColor?` where `X` is the class itself.
		if not self.doc: return None if DRYDOC else 'property for internal use only'
		s = WrapEachParagraph( self.doc.format( cls=self.owner ) ).strip() + '\n'
		thisToIt = lambda s: re.sub( r'^(`\.?%s`|This)(?= is)' % self.name, 'It', s )
		if SPHINXDOC: s = 'This is a :ref:`managed property <ManagedProperties>`.\n' + thisToIt( s )
		else: s = 'This is a managed property - see `Shady.Documentation.ManagedPropertiesAndShortcuts`.\n\n' + thisToIt( s )
		s += '\n* Default value:  '
		default_string = getattr( self, 'default_string', '' )
		if default_string:
			s += default_string
		else:
			n = numel( self.default )
			if n == 1: s+= '`{}`'.format( self.default[ 0 ] )
			elif n <= 16: s += '`{}`'.format( list( self.default ) )
			elif len( set( self.default ) ) == 1: s += '`{} * {}`'.format( list( self.default[ :1 ] ), len( self.default ) )
			else: s += '`' + str( list( self.default[ :3 ] ) ).replace( ']', ', ...]' ) + '` (length {})'.format( n )
		if len( self.names ) > 1: s += '\n* Canonical name: `.%s`' % self.name
		if len( self.names ) > 1: s += '\n* Other aliases:  ' + '  '.join( '`.%s`' % name for name in self.names[ 1: ] )
		if self.shortcuts: s += '\n* Subscripting shortcuts:' + ''.join( '\n   * ' + shortcut.brief_doc( True ) for index, shortcut in sorted( self.shortcuts.items() ) )
		return s
	def __get__( self, instance, owner ):
		if instance is None: return self
		array = self.determine_array( instance )
		if numel( array ) == 1:
			try: array.flat
			except: return self.scalarWrapper( array[ 0 ] )
			else: return self.scalarWrapper( array.flat[ 0 ] )
		else: return array
	def __set__( self, instance, value ):
		name = self.names[ 0 ]
		if callable( value ): return instance.SetDynamic( name, value, order=self.order, canonicalized=True )
		if value is instance: return instance.MakePropertiesIndependent( name )
		if isinstance( getattr( type( value ), name, None ), ManagedProperty ): return value.ShareProperties( instance, name )
		instance.SetDynamic( name, None, canonicalized=True )
		array = self.determine_array( instance, name=name )
		recordChange = instance._RecordChange
		if recordChange: recordChange( instance, name, old=array, new=value )
		try: array.flat
		except: assign_sequence( array, value )
		else: array.flat = value
	def __getitem__( self, s ):
		if isinstance( s, slice ): return [ self[ i ] for i in range( *s.indices( numel( self.default ) ) ) ]
		if s not in self.shortcuts: self.shortcuts[ s ] = ManagedShortcut( self, s )
		return self.shortcuts[ s ]
	def __iter__( self ):
		for i in range( numel( self.default ) ): yield self[ i ]
	def SetDefault( self, value ):
		try: self.default.flat
		except: assign_sequence( self.default, value )
		else: self.default.flat = value
		self.default_changed = True
		return self
	
	def rst( self, parentClassName ):
		s = ' = '.join( self.names )
		s = '* :py:obj:`%s <%s.%s>`' % ( self.names[ 0 ], parentClassName, self.names[ 0 ] )
		for name in self.names[ 1: ]:  s += ' = ``%s``' % name
		if self.shortcuts: s += ' = ``[' + ','.join( '%s' % v.name for k, v in sorted( self.shortcuts.items() ) ) + ']``'
		return s
	
class ManagedShortcut( object ):
	def __init__( self, prop, index ):
		"""
		For general information about the ManagedShortcut descriptor
		class, see either:
		    * :ref:`the online documentation on managed properties and
		      shortcuts <ManagedProperties>`
		    * or: the docstring of `Shady.Documentation.ManagedPropertiesAndShortcuts`
		"""
		SHORTCUTS_TMP.append( self )
		self.order_defined = len( SHORTCUTS_TMP )
		self.__prop = [ prop ]
		self.index = index
		self.names = []
		self.owner = '{cls}'
		self.note = ''
		self.scalarWrapper = MakeScalarWrapper( self, prop.default[ 0 ] )
		self.custom = False
	@property
	def parent( self ):
		return self.__prop[ 0 ]
	@property
	def name( self ):
		return self.names[ 0 ] if self.names else None
	@name.setter
	def name( self, value ):
		if value in self.names: del self.names[ self.names.index( value ) ]
		if value: self.names.insert( 0, value )
	def brief_doc( self, align=False ):
		s = '{name} is a shortcut for `.{parentName}[{index}]`'
		if SPHINXDOC: s = s.replace( '[', '`\\ `[' )
		if align: s = s.replace( '{name}', '{name:%ds}' % max( 3 + len( sh.name ) for sh in self.__prop[ 0 ].shortcuts.values() ) )
		s = s.format( name='`.' + self.name + '`', parentName=self.__prop[ 0 ].name, index=self.index )
		if self.note: s += ' ({note})'.format( note=self.note )
		return s
	@property
	def __doc__( self ):
		s = self.brief_doc()
		thisToIt = lambda s: re.sub( r'^(`\.?%s`|This)(?= is)' % self.name, 'It', s )
		if SPHINXDOC: s = 'This is a :ref:`managed shortcut <ManagedShortcuts>`.\n' + thisToIt( s )
		else: s = 'This is a managed shortcut - see `Shady.Documentation.ManagedPropertiesAndShortcuts`.\n\n' + thisToIt( s )
		if len( self.names ) > 1: s += '\n\n* Canonical name: `.%s`' % self.name
		if len( self.names ) > 1: s += '\n* Other aliases:  ' + '  '.join( '`.%s`' % name for name in self.names[ 1: ] )
		parentDoc = self.__prop[ 0 ].__doc__
		if parentDoc and not DRYDOC: s += '\n\nDocumentation for the full `.{parentName}` property:{parentDoc}'.format( parentName=self.__prop[ 0 ].name, parentDoc=( '\n' + parentDoc ).replace( '\n', '\n    ' ) )
		return s
	def __get__( self, instance, owner ):
		if instance is None: return self
		value = self.__prop[ 0 ].__get__( instance, owner )[ self.index ]
		return self.scalarWrapper( value )
	def __set__( self, instance, value ):
		name = self.names[ 0 ]
		if callable( value ): return instance.SetDynamic( name, value, order=self.order, canonicalized=True )
		correspondingAttribute = getattr( type( value ), name, None )
		if isinstance( correspondingAttribute, ( ManagedProperty, ManagedShortcut ) ):
			raise TypeError( 'cannot assign .%s = instance as a shortcut for property linking, because .%s is not a fully-fledged property - it is only a shortcut to part of the .%s property ' % ( name, name, correspondingAttribute.parent.name ) )
		instance.SetDynamic( name, None, canonicalized=True )
		array = self.__prop[ 0 ].__get__( instance, type( instance ) )
		index = self.index
		recordChange = instance._RecordChange
		if recordChange: recordChange( instance, name, old=array[ index ], new=value )
		array[ index ] = value
	def __repr__( self ):
		s = '<{cls} object at 0x{id:08x}>'.format( cls=self.__class__.__name__, id=id( self ) )
		if self.names: s += ': ' + '|'.join( self.names )
		s += ' = {target}[{index}]'.format( index=self.index, target=self.__prop[ 0 ].name )
		return s
	def SetDefault( self, value ):
		self.__prop[ 0 ].default_changed = True
		self.__prop[ 0 ].default[ self.index ] = value
		return self
