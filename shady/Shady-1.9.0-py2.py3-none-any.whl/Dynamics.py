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
"""
The Dynamics module contains a number of objects that are
designed to perform discretized real-time processing of
arbitrary functions.

The most general-purpose object is the `Function` which is
a type of callable that supports arithmetic and other tricks.

Various wrapper functions act as factories for `Functions`
configured with specialized behavior (most of them with
memory for previous inputs). For example:

* `Integral` and `Derivative` perform discrete calculus on
  their inputs.

* `Smoother` smooths its input

* `Transition` provides a transient (self-removing, once
  complete) dynamic.
  
* `Oscillator` provides sinusoidally varying output

The other major contribution is `StateMachine` a different
class that provides callable instances in which discrete-
time state-machine logic cna easily be implemented.

Note that everything exported from this module is also available in
the top-level `Shady.*` namespace.
"""


__all__ = [
	'Clock',
	'Function',
	'Integral', 'Derivative', 'ResetTimeBase',
	'Impulse', 'Smoother',
	'Sinusoid', 'Oscillator',
	'Transition', 'RaisedCosine',
	'TimeOut', 'Sequence', 'Forever', 'CallOnce', 'WaitUntil', 'STITCH',
	'Apply',
	'StateMachine',
]

import copy
import math
import inspect
import weakref
import operator
import itertools
import functools
import collections

numpy = None
try: import numpy
except: pass

IDCODE = property( lambda self: '0x%08x' % id( self ) )

class Constant( object ):
	def __init__( self, name, doc=None ): self.__name, self.__doc = name, doc
	def __repr__( self ): return self.__name
	__doc__ = property( lambda self: self.__doc )

class Stop( StopIteration ):
	"""
	This a type of `Exception` - specifically, a subclass of `StopIteration`.
	It is raised internally when a `Function`'s "watcher" callback (set using
	`Function.Watch()`) returns a numeric argument, or a numeric sequence
	or array).  The `Function` will continue to transform this terminal value
	according to its existing chain, but at the very last stage of the chain
	it will throw another `Stop()` containing the transformed terminal value.
	
	Some frameworks (e.g. `Shady.PropertyManagement`) will automatically catch
	and deal with this type of exception.
	"""
	def __init__( self, arg ): StopIteration.__init__( self, arg )
	
class Abort( StopIteration ):
	"""
	This a type of `Exception` - specifically, a subclass of `StopIteration`.
	It is raised when a `Function`'s "watcher" callback (set using
	`Function.Watch()`) returns a `dict` argument. Unlike a `Stop` exception,
	the `Function` chain will not catch, transform and re-throw this type
	of exception.
	
	Some frameworks (e.g. `Shady.PropertyManagement`) will automatically catch
	and deal with this type of exception.
	"""
	def __init__( self, arg ): StopIteration.__init__( self, arg )
	
class Function( object ):
	"""
	A `Function` instance is a callable wrapper around another
	callable and/or around a constant.  `Function` objects support
	arithmetic operators.

		f = Function( lambda t: t ** 2 ) + Function( lambda t: t )
		g = lambda t: t ** 2 + t

	`f` and `g` are both callable objects and both will return the
	same result when called with a numeric argument. `f` is of
	course less efficient than `g`. However, it allows functions
	to be defined and built up in a modular way
	
	Args:
		*pargs
			Each of the positional arguments is considered to be a
			separate additive :term".  Terms (or their outputs, if
			callable) are added together when the `Function` is
			called.
			
		**kwargs
			If supplied, any optional keyword arguments are passed
			through to every callable term, whenever the `Function`
			is called.
	"""
	__slots__ = [ 'terms' ]
	id = IDCODE
	
	def __init__( self, *pargs, **kwargs ):
		if not hasattr( self, 'terms' ): self._init( *pargs, **kwargs )	
	def _init( self, *pargs, **kwargs ):
		self.terms = []
		while pargs:
			other = pargs[ 0 ]
			if type( self ) is not type( other ): break
			pargs = pargs[ 1: ]
			self.terms[ : ] = copy.deepcopy( other.terms ) # efficiency hack to reduce the occurrence of wrappers of wrappers of wrappers
			if self.terms: break
		for arg in pargs:
			if kwargs and callable( arg ): arg = functools.partial( arg, **kwargs )
			self += arg
		return self

	def __call__( self, *pargs, **kwargs ):
		#print('%r is being called with %r and %r' % ( self, pargs, kwargs ))
		result = None
		stopped = False
		for mode, opfunc, term in self.terms:
			if mode == 'through':
				pp, kk = opfunc
				opfunc = None
				term = term( result, *pp, **kk )
			elif mode == 'watch':
				if result is None: continue
				pp, kk = opfunc
				opfunc = None
				stopValue = term( result, *pp, **kk )
				if stopValue is None: continue
				if isinstance( stopValue, dict ): raise Abort( stopValue )
				term = stopValue
				stopped = True
			elif callable( term ):
				try: term = term( *pargs, **kwargs )
				except Stop as exc:
					term = exc.args[ 0 ]
					stopped = True
			if isinstance( term, Exception ): raise term
			if numpy is not None and term is not None and not isinstance( term, ( int, float, complex, str, numpy.ndarray ) ):
				try: term = numpy.array( term, dtype=float, copy=False )
				except: term = numpy.array( term, dtype=complex, copy=False )
			if result is None or opfunc is None: result = term
			elif mode == 'LR':  result = opfunc( result, term )
			elif mode == 'RL':  result = opfunc( term, result )
			else: raise ValueError( 'internal error - unexpected mode' )
		if stopped: raise Stop( result )
		return result
	
	def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
	def __str__( self ):
		s = repr( self )
		for iTerm, ( mode, opfunc, term ) in enumerate( self.terms ):
			isLast = ( iTerm == len( self.terms ) - 1 )
			if mode == 'through':
				pp, kk = opfunc
				s += TreeBranch( 'through %s( <>%s%s )' % ( term.__name__, ''.join( ', %r' % arg for arg in pp ), ''.join( ', %s=%r' % item for item in kk.items() ) ) )
			else:
				if iTerm: s += TreeBranch( '%s %r' % ( mode, opfunc ) )
				s += TreeBranch( term, last=isLast )
		return s
		
	def __neg__( self ): return 0 - self
	def __pos__( self ): return self
	def __abs__( self ): return self.Transform( abs )
	
	def Transform( self, any_callable, *additional_pargs, **kwargs ):
		"""
		Arithmetic operations on a `Function` build up a chain of
		operations.  For example::
		
			f = Function( lambda t: t )
			f += 1  # Now f(t) will return t + 1
			f *= 2  # Now f(t) will return 2 * t + 2
		
		The `Transform` method allows arbitrary operations to be
		added to the chain. For example::
		
			f.Transform( math.sin )
			# Now f(t) will return math.sin( 2 * t + 2 )
		
		Any `*additional_pargs` or `**kwargs` are passed through
		to the transforming function (`any_callable`).
		
		The `.Transform()` method changes the `Function` instance
		in-place, in a manner analogous to `+=` and `*=`.   By
		contrast, binary operators `*` and `+` return a new
		`Function` containing deep copies of the original instance's
		terms. As `+` is to `+=`, so the global function `Apply()`
		is to the `.Transform()` method::
		
			f = Function( lambda t: t )
			g = Apply( math.cos, f )  # creates a separate `Function` instance
			f.Transform( math.sin )   # transforms `f` in-place
			
			# now g(t) returns math.cos(t) and f(t) returns math.sin(t)
			
		"""
		if isinstance( any_callable, str ): self.terms.append( ( 'RL', operator.mod, any_callable ) )
		else: self.terms.append( ( 'through', ( additional_pargs, kwargs ), any_callable ) )
		return self
	Through = Transform
	
	
	def Watch( self, conditional, *additional_pargs, **kwargs ):
		"""
		Adds a watch condition on the output of a `Function`.
		
		Args:
		
		    conditional (callable):
		        This should be a callable whose first input
		        argument is a `float`, `int` or numeric `numpy`
		        array.  The return value can be:
		        
		        * `None`, in which case nothing happens
		        
		        * a `dict` `d`, in which case the `Function`
		          will raise an `Abort` exception (a subclass
		          of `StopIteration`) containing `d` as the
		          exception's argument.  The `Function` itself
		          will not perform any further processing.
		          
		        * a numeric value (or numeric array) `x`, in
		          which case the `Function` will continue to
		          process the numeric value but, at the very
		          last step in the chain, it will raise a
		          `Stop` exception (a subclass of
		          `StopIteration`) containing the final
		          processed value.
		
		    *additional_pargs:
		        If additional positional arguments are supplied,
		        they are simply passed through to `conditional`.
		        
		    **kwargs:
		        If additional keyword arguments are supplied,
		        they are simply passed through to `conditional`.
		
		Some frameworks (e.g. `Shady.PropertyManagement`) will
		automatically catch and deal with `StopIteration` exceptions
		appropriately, but if you need to do so manually, you can do
		so as follows::
		
		    try:
		        y = f( t )
		    except StopIteration as exc:
		        info = exc.args[ 0 ]
		        if not isinstance( info, dict ):
		            terminal_value_of_y = info
		"""
		#TODO: need a demo of this in conjunction with PropertyManagement/Shady dynamics:
		#      functionInstance.Watch(
		#          lambda f:  None if f < 10 else {'visible':0}
		#      )
		self.terms.append( ( 'watch', ( additional_pargs, kwargs ), conditional ) )
		return self
	
	def Tap( self, initial=None ):
		"""
		As you transform a `Function` object, you develop a pipeline
		of successively applied operations.  What if you want to
		examine values at an intermediate stage along that pipeline?
		In this case you can `.Tap()` it.  The result is a callable
		object that you can call to obtain the latest value.
		
		Example::
		
			f = Function( lambda t: t )
			f *= 2
			f += 2
			intermediate = f.Tap() 
			f.Transform( math.sin )
		
			for input_value in [ 0.1, 0.2, 0.3, 0.4, 0.5 ]:
				output_value = f( input_value )
				print( '            t  = %r' % input_value     )
				print( '    2 * t + 2  = %r' % intermediate()  )
				print( 'sin(2 * t + 2) = %r' % output_value    )
				print( '' )
		
		"""
		return Tap( self, initial=initial )

class Tap( object ):
	def __init__( self, f, initial=0.0 ): self.container = [ initial ]; f.Watch( self._watch )
	def _watch( self, result ): self.container[ : ] = [ result ]
	def __call__( self ): return self.container[ 0 ]
		
def TreeBranch( txt, spacers=1, last=False ):
	blank   = '       '
	bar     = ' |     '
	branch  = ' +---- '
	indent  = blank if last else bar
	lines = str( txt ).replace( '\r\n', '\n' ).replace( '\r', '\n' ).split( '\n' )
	s = ( '\n' + bar ) * spacers + '\n'
	return s + '\n'.join( ( indent if iLine else branch ) + line for iLine, line in enumerate( lines ) )

def MakeOperatorMethod( optype, opname ):
	if opname == 'div': opname = 'truediv'
	opfunc = getattr( operator, opname + '_', None )
	if opfunc is None: opfunc = getattr( operator, opname )
	def func( instance, other ):
		if optype == 'i':
			mode = 'LR'
		else:
			if   optype == 'l': mode = 'LR'
			elif optype == 'r': mode = 'RL'
			else: raise ValueError( 'internal error - unexpected mode' )
			instance = copy.deepcopy( instance )
		if getattr( other, '_SHADY_COPYABLE', True ): other = copy.deepcopy( other )
		instance.terms.append( ( mode, opfunc, other ) )
		return instance
	return func

def _DoNotCopy( obj ):
	obj._SHADY_COPYABLE = False
	return obj

for opname in 'add sub mul truediv div floordiv pow mod and or xor'.split():
	setattr( Function, '__'  + opname + '__', MakeOperatorMethod( 'l', opname ) )
	setattr( Function, '__r' + opname + '__', MakeOperatorMethod( 'r', opname ) )
	setattr( Function, '__i' + opname + '__', MakeOperatorMethod( 'i', opname ) )

def Apply( any_callable, f, *additional_pargs, **kwargs ):
	"""
	::
	
		g = Apply( some_function, f )   # `f` is a `Function` instance
		                                # and now so is `g`
	
	is equivalent to::
	
		g = copy.deepcopy( f ).Transform( some_function )
	
	In both cases, `some_function()` is applied to transform the output
	that `f` would otherwise have given, but whereas the `.Transform()`
	method actually alters the original instance `f`,  `Apply` creates
	a new `Function` instance and leaves the original `f` untouched.
	
	See also: `Function.Transform`
	"""
	return copy.deepcopy( f ).Transform( any_callable, *additional_pargs, **kwargs )

def Impulse( magnitude=1.0, autostop=True ):
	"""
	This function constructs a very simple specially-configured `Function`
	instance, which will return `magnitude` the first time it is called
	(or when called again with the same `t` argument as its first call)
	and then return `0.0` if called with any other value of `t`.
	"""
	_t0 = [ None ]
	def impulse_core( t, *pargs, **kwargs ):
		t0 = _t0[ 0 ]
		if t0 is None: t0 = _t0[ 0 ] = t
		if t == t0: return magnitude
		elif autostop: raise Stop( 0.0 )
		else: return 0.0
	return Function( impulse_core )

def Sinusoid( cycles, phase_deg=0 ):
	"""
	Who enjoys typing `2.0 * numpy.pi *` over and over again?
	This is a wrapper around `numpy.sin` (or `math.sin` if `numpy`
	is not installed) which returns a sine function of an argument
	expressed in cycles (0 to 1 around the circle).  Heterogeneously,
	but hopefully intuitively, the optional phase-offset argument
	is expressed in degrees. If `numpy` is installed, either
	argument may be non-scalar (`phase_deg=[90,0]` is useful for
	converting an angle into 2-D Cartesian coordinates).
	
	This is a function,  but not a `Function`.  You may be
	interested in `Oscillator`, which returns a `Function`
	wrapper around this.
	"""
	if numpy: return numpy.sin( 2.0 * numpy.pi * ( numpy.asarray( cycles, float ) + numpy.asarray( phase_deg, float ) / 360.0 ) )
	else:     return math.sin(  2.0 * math.pi  * ( float( cycles )                + float( phase_deg )                / 360.0 ) )
		
def Oscillator( freq, phase_deg=0.0 ):
	"""
	Returns a `Function` object with an output that oscillates
	sinusoidally as a function of time: the result of `Apply()`-ing
	`Sinusoid` to an `Integral`.
	"""
	return Apply( Sinusoid, Integral( freq ), phase_deg=phase_deg )

def Clock( startNow=True, speed=1.0 ):
	"""
	This function returns a `Function` wrapped around a 
	simple linear callable that takes one argument `t`.
	
	Args:

		startNow (bool)
			If this is `True`, the clock's time zero starts
			the first time it is called. If it is `False`,
			the clock does not subtract any "time zero",
			but rather just uses the `t` argument that is
			passed to it.
			
		speed (float )
			This specifies the speed at which the clock
			runs---it's just a multiplier applied to the
			input vaue `t`.
				
	If `startNow=True` you can get the same effect with
	`f = Integral( speed )` but the implementation in `Clock()`
	is simpler and hence a little more efficient. Note that,
	because of this simplicity, `ResetTimeBase` will not
	work on this object.
	"""
	if numpy: speed = numpy.asarray( speed, dtype=float )
	if startNow:
		t0 = []
		def clock( t ):
			if not t0: t0.append( t )
			return speed * ( t - t0[ 0 ] )
	else:
		clock = lambda t: speed * t
	return Function( clock )

def Smoother( arg=None, sigma=1.0, exponent='EWA' ):
	"""
	This function constructs a `Function` instance that smooths, with
	respect to time, the numeric output of whatever callable object it
	wraps.  You could test this by wrapping the output of `Impulse()`
	with it.
	
	Args:
		
		arg
			A `Function` instance or any other callable that returns
			a numeric output.
		
		sigma
			Interpreted as a the sigma (width) parameter of a Gaussian
			if `exponent` is 2.0 (or of the comparable exponential-family
			function if it is some other positive numeric value).
			If `exponent` is not numeric, `sigma` is interpreted as the
			half-life of an exponential-weighted-average (EWA) smoother.
			
		exponent
			If this is `None` or the string `'EWA'` then the `Smoother`
			uses exponential weighted averaging, with `sigma` as its
			half-life.  Alternatively, if this is a positive floating-
			point value, it is treated as the exponent of an
			exponential-family function for generating finite-impulse-
			response weights, with sigma as the time-scale parameter.
			`exponent=2.0` gets you Gaussian-weighted FIR coefficients.
	
	Returns:
		A `Function` instance.
	
	"""
	return Function( _SmoothingWrapper( arg, sigma=sigma, exponent=exponent ) )

@_DoNotCopy
class _SmoothingWrapper( object ):
	__slots__ = [ 'func', 'sigma', 'exponent', 'memory', 'lastOutput' ]
	id = IDCODE
	def __init__( self, func, sigma, exponent ):
		self.memory = {}
		self.func = func
		self.sigma = float( sigma )
		if isinstance( exponent, str ) and exponent.lower() == 'ewa': exponent = None 
		self.exponent = exponent
		self.lastOutput =  None
	def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
	def __str__( self ): return repr( self ) + TreeBranch( self.func, last=True )
	def __call__( self, t, *pargs, **kwargs ):
		if t is None: return self.lastOutput
		x, y = self.memory.get( t, ( None, None ) )
		if y is not None: self.lastOutput = y; return y
		if x is None:
			x = self.func
			if callable( x ): x = x( t, *pargs, **kwargs )
		if numpy: x = numpy.array( x, dtype=float, copy=True )
		if x is None or not self.sigma: self.lastOutput = x; return x
		self.memory[ t ] = ( x, None )
		if self.exponent is None: y = self.EWA( t )
		else: y = self.FIR( t )
		self.memory[ t ] = ( x, y )
		self.lastOutput = y
		return y
		
	def FIR( self, t ): # Gaussian-weighted with sigma interpreted as standard deviation
		sumwx = sumw  = 0.0
		for ti, ( xi, yi ) in list( self.memory.items() ):
			nsig = abs( t - ti ) / self.sigma
			if nsig > 5.0: del self.memory[ ti ]; continue
			if self.sigma == 0.0: wi = 1.0
			else: wi = math.exp( -0.5 * nsig ** self.exponent )
			sumw  = sumw  + wi
			sumwx = sumwx + wi * xi
		return sumwx / sumw			
	def EWA( self, t ): # exponential weighted average (IIR of order 1) with sigma interpreted as half-life
		items = sorted( self.memory.items() )
		tcurr, ( xcurr, ycurr ) = items[ -1 ]
		if len( items ) == 1: return xcurr
		tprev, ( xprev, yprev ) = items[ -2 ]
		self.memory = dict( items[ -2: ] )
		lambda_ = 0.5 ** ( ( tcurr - tprev ) / self.sigma )
		return lambda_ * yprev + ( 1.0 - lambda_ ) * xcurr
			
			
def Integral( *pargs, **kwargs ):
	r"""
	Returns a specially-configured `Function`. Like the `Function` constructor,
	the terms wrapped by this call may be numeric constants, and/or callables that
	take a single numeric argument `t`.   And like any `Function` instance, the
	instance returned by `Integral` is itself a callable object that can be
	called with `t`.
	
	Unlike a vanilla `Function`, however, an `Integral` has memory for values
	of `t` on which it has previously been called, and returns the *cumulative*
	area under the sum of its wrapped terms, estimated discretely via the
	trapezium rule at the distinct values of `t` for which the object is called.
	
	Like any `Function`, it can interact with other `Functions`, with other
	single-argument callables, with numeric constants, and with numeric
	`numpy` objects via the standard arithmetic operators `+`, `-`, `/`,
	`*`, `**`, and `%`, and may also have other functions applied to its
	output via `Apply`.
	
	`Integral` may naturally be take another `Integral` output as its input,
	or indeed any other type of `Function`.
	
	Example - prints samples from the quadratic :math:`\frac{1}{2}t^2 + 100`:: 
	    
	    g = Integral( lambda t: t ) + 100.0
	    print( g(0) )
	    print( g(0.5) )
	    print( g(1.0) )
	    print( g(1.5) )
	    print( g(2.0) )
	
	"""
	if not pargs: pargs = ( 1.0, ) 
	integrate = kwargs.pop( 'integrate', 'trapezium' )
	if integrate not in [ 'trapezium', 'rectangle' ]: raise ValueError( '`integrate` argument must be "trapezium" or "rectangle"' )
	initial = kwargs.pop( 'initial', 0.0 )
	return Function( *[ _DiscreteCalculusWrapper( arg, integrate=integrate, initial=initial ) for arg in pargs ], **kwargs )

def Derivative( *pargs, **kwargs ):
	"""
	Like `Integral()`, but configures its `Function` to perform
	discrete-time differentiation instead of integration.
	"""
	if not pargs: pargs = ( 1.0, ) 
	return Function( *[ _DiscreteCalculusWrapper( arg, integrate=False ) for arg in pargs ], **kwargs )

def ResetTimeBase( x ):
	"""
	This method can be applied to `Function` and `StateMachine`
	instances. It will run through the `.terms` of the `Function`
	(and recursively through all the `.terms` of any terms that
	are themselves `Function`s) looking for dynamic objects that
	have memory: `StateMachine`, and `Function` wrappers produced
	by `Integral`, `Derivative`, `TimeOut`, `Transition` or
	`Smoother`.  In any of these cases, it erases their memory of
	previous calls.  They (and hence the `Function` as a whole)
	will consider the next `t` value they receive to be "time zero".
	"""
	if isinstance( x, _DiscreteCalculusWrapper ):
		x.t_prev = None
		ResetTimeBase( x.func )
	elif isinstance( x, _SmoothingWrapper ):
		x.memory.clear()
		ResetTimeBase( x.func )
	elif isinstance( x, ( _TimeOut, _Transition ) ):
		x.t_prev = None
		x.t0 = None
	elif isinstance( x, _Sequence ):
		raise TypeError( 'cannot call ResetTimeBase on a Sequence' )
	elif isinstance( x, StateMachine ):
		raise TypeError( 'cannot call ResetTimeBase on StateMachine' )
	else:
		for mode, opfunc, term in getattr( x, 'terms', [] ): ResetTimeBase( term )

@_DoNotCopy
class _DiscreteCalculusWrapper( object ):
	__slots__ = [ 'func', 't_prev', 'f_prev', 'y', 'integrate' ]
	id = IDCODE
	def __init__( self, func, integrate, initial=0.0 ):
		#print( '_Accumulator.__init__(%r, %r)' % ( self, func ) )
		self.func = func
		self.t_prev = None
		self.f_prev = None
		self.integrate = integrate
		self.y = initial
		if numpy and not isinstance( initial, ( int, float, complex ) ):
			try:    self.y = numpy.array( initial, dtype=float,   copy=True )
			except: self.y = numpy.array( initial, dtype=complex, copy=True )
	def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
	def __str__( self ): return repr( self ) + TreeBranch( self.func, last=True )
	def __call__( self, t, *pargs, **kwargs ):
		#print('%r is being called with %r, %r and %r' % ( self, t, pargs, kwargs ))
		if t is None: return self.y
		if self.t_prev is None: dt = None
		else: dt = t - self.t_prev
		self.t_prev = t
		value = self.func
		if callable( value ):
			#print( '%r is calling %r with %r, %r and %r' % ( self, value, t, pargs, kwargs ) )
			value = value( t, *pargs, **kwargs )
		if isinstance( value, Exception ): raise value
		if numpy is not None and value is not None and not isinstance( value, ( int, float, numpy.ndarray ) ):
			value = numpy.array( value, dtype=float, copy=False )
		try: ysize = self.y.size
		except: ysize = 1
		try: vsize = value.size
		except: vsize = 1
		if dt is None and numpy and ysize == 1 and vsize > 1:
			self.y = numpy.zeros_like( value ) + self.y
		elif dt:
			if self.integrate == 'trapezium': self.y += ( value + self.f_prev ) * 0.5 * dt # adds trapezia (i.e. assume the function value climbed linearly to its current value over the interval since last call)
			elif self.integrate: self.y += value * dt # adds rectangles (i.e. assumes that the function took a step up to its current value immediately after the last call)
			else: self.y = ( value - self.f_prev ) / dt
		if dt or self.f_prev is None: self.f_prev = value
		return self.y

COS = numpy.cos if numpy else math.cos
PI  = numpy.pi  if numpy else math.pi
def RaisedCosine( x ):
	"""
	Maps a linear ramp from 0 to 1 onto a raised-cosine rise from
	0 to 1.  Half a Hann window.
	"""
	return 0.5 - 0.5 * COS( x * PI )

def Transition( start=0.0, end=1.0, duration=1.0, delay=0.0, transform=None, finish=None ):
	"""
	This is a self-stopping dynamic. It uses a `Function.Watch()`
	call to ensure that, when the dynamic reaches its `end` value,
	a `Stop` exception (a subclass of `StopIteration`) is raised.
	Some frameworks (e.g. `Shady.PropertyManagement`) will
	automatically catch and deal with `StopIteration` exceptions.
	
	Args:
		start (float, int or numeric numpy.array):
			initial value
			
		end (float, int or numeric numpy.array):
			terminal value
			
		duration (float or int):
			duration of the transition, in seconds
	
		delay (float or int):
			delay before the start of the transition, in seconds
	
		transform (callable):
			an optional single-argument function that takes in
			numeric values in the domain [0, 1] inclusive, and
			outputs numeric values. If you want the final output
			to scale correctly between `start` and `end`, then the
			output range of `transform` should also be [0, 1].
			
		finish (callable):
			an optional zero-argument function that is called when
			the transition terminates
	
	Example::
	
		from Shady import World, Transition, RaisedCosine, Hann
		
		w = World( canvas=True, gamma=-1 )
		gabor = w.Sine( pp=0, atmosphere=w )
		
		@w.EventHandler( slot=-1 )
		def ControlContrast( self, event ):
			if event.type == 'key_release' and event.key == 'r':
				gabor.contrast = Transition( transform=RaisedCosine )
			if event.type == 'key_release' and event.key == 'f':
				gabor.contrast = Transition( 1, 0, transform=RaisedCosine )
			if event.type == 'key_release' and event.key == 'h':
				gabor.contrast = Transition( duration=2, transform=Hann )
		
		# press 'f' to see contrast fall from 1 to 0 using a raised-cosine
		# press 'r' to see contrast rise from 0 to 1 using a raised-cosine
		# press 'h' to see contrast rise and fall using a Hann window in time
	
	"""
	return Function( _Transition( start=start, end=end, duration=duration, delay=delay, transform=transform, finish=finish ) )
	
@_DoNotCopy
class _Transition( object ):
	def __init__( self, start=0.0, end=1.0, duration=1.0, delay=0.0, transform=None, finish=None ):
		self.t0 = None
		self.t_prev = None
		self.f_prev = None
		self.transform = transform
		self.finish = finish
		if numpy:
			self.start    = numpy.array( start,    dtype=float )
			self.end      = numpy.array( end,      dtype=float )
			self.delay    = numpy.array( delay,    dtype=float )
			self.duration = numpy.array( duration, dtype=float )
			with numpy.errstate( divide='ignore' ): self.speed = 1.0 / self.duration
			self.max = numpy.maximum
			self.min = numpy.minimum
			self.all = numpy.all
		else:
			self.start    = float( start )
			self.end      = float( end )
			self.delay    = float( delay )
			self.duration = float( duration )
			self.speed = 1.0 / self.duration if self.duration else float( 'inf' )
			self.max = max
			self.min = min
			self.all = lambda x: x
	def __call__( self, t ):
		if self.t0 is None: self.t0 = t
		if t == self.t_prev: return self.f_prev
		self.t_prev = t
		t = float( t ) - self.t0 - self.delay
		t = self.max( 0.0, t )
		if numpy:
			# the edge cases here are really the reason this class exists instead of the previous implementation that used a Function chain)
			#t = numpy.multiply( t, self.speed, where=( t != 0 ), out=numpy.zeros_like( t + speed ) ) # would also work but has less support for antiquated numpy versions, so let's do it this way:
			with numpy.errstate( invalid='ignore' ): t = numpy.array( t * self.speed )
			ravelled = t.ravel()
			ravelled[ numpy.isnan( ravelled ) ] = 0.0
		else:
			if t: t *= self.speed
		t = self.min( 1.0, t )
		stop = self.all( t == 1.0 )
		if self.transform: t = self.transform( t )
		self.f_prev = f = ( 1.0 - t ) * self.start + t * self.end
		if stop:
			if self.finish: self.finish()
			raise Stop( f )
		return f

@_DoNotCopy
class _TimeOut( object ):
	def __init__( self, func, duration ):
		self.func = func
		self.duration = duration
		self.t0 = None
		self.t_prev = None
		self.f_prev = None
	def __call__( self, t ):
		if self.t0 is None: self.t0 = t
		if t == self.t_prev: return self.f_prev
		self.t_prev = t
		value = self.f_prev = self.func( t )
		if t > self.t0 + self.duration: raise Stop( value )
		return value
		
def TimeOut( func, duration ):
	"""
	Returns a wrapped version of callable `func` that
	raises a `Stop` exception when called with a `t`
	argument larger than the very first `t` argument it
	receives plus `duration`.
	"""
	return Function( _TimeOut( func, duration ) )

def Sequence( container ):
	"""
	Returns a `Function` object whose value is defined piecewise by the
	elements of `container`.  The `container` may be:
	
	- a `dict` whose keys are numbers: the keys are interpreted as
	  time-points relative to the first time the `Function` is called,
	  and they dictate the times at which the `Function` output should
	  switch to the corresponding value. If any value is itself a
	  callable object, then the overall `Function` output is computed
	  by calling it, with the relative time-since-first call as its
	  single argument.
	
	- any other iterable: the items are then simply handled in turn,
	  each time the `Function` is called with a new value for the time
	  `t` argument. If any item is itself a callable object, then the
	  overall `Function` output is computed by calling it, with the
	  relative time-since-first call as its single argument---also, we
	  do not advance to the next item until that item has raised a
	  `StopIteration` exception.  This allows you to chain
	  `Transition()` function objects together---e.g.::
	  
	      Sequence( [ Transition( 0, 100 ), Transition( 100, 0 ) ] )
	
	  You can also use the constant `STITCH` to ensure that the terminal
	  value from the preceding callable is ignored---so in the following
	  example, the value 100 would not be repeated::
	  
	      Sequence( [ Transition( 0, 100 ), STITCH, Transition( 100, 0 ) ] )
	      
	See also: `CallOnce`, `WaitUntil`, `TimeOut`, `STITCH`
	"""
	return Function( _Sequence( container ) )

Forever = itertools.count

def CallOnce( func ):
	"""
	Can be used in a `Sequence` to create a side effect. For example::
	
		def Foo():
			print( 'The sequence has ended' )
	
		f = Sequence( [ Transition( 0, 1 ), Transition( 1, 0 ), CallOnce( Foo ) ] )
		import numpy
		for t in numpy.arange( 0, 3, 0.01): print(f(t))
	
	See also: `Sequence`, `WaitUntil`, `TimeOut`, `STITCH`
	"""
	def wrapped( _ ): raise Stop( func() )
	return wrapped
    
def WaitUntil( func, ongoingValue=None, finalValue=None ):
	"""
	Can be used in a `Sequence` to hold until a certain condition is fulfilled
	(signalled by `func()` returning a truthy value).
	
	See also: `Sequence`, `CallOnce`, `TimeOut`, `STITCH`
	"""
	def wrapped( _ ):
		if func(): raise Stop( finalValue )
		return ongoingValue
	return wrapped


STITCH = Constant( 'STITCH', """\
A constant that can be used in a `Sequence` to stitch two callable functions together.
It causes any final value (thrown inside a `Stop` or other `StopIteration` exception)
of the preceding callable to be ignored.  See `Sequence` for an example. """ )
@_DoNotCopy
class _Sequence( object ):
	def __init__( self, container ):

		if isinstance( container, dict ):
			self.items = iter( sorted( container.items() ) )
		else:
			self.items = getattr( itertools, 'izip', zip )( itertools.repeat( None ), container )
		
		self.t_prev = None
		self.f_prev = None
		self.t0 = None
		self.currentPiece = None
		self.buffered = []
		self.Buffer()
		
	def Buffer( self ):
		if not self.buffered:
			try:
				self.buffered.append( next( self.items ) )
			except StopIteration:
				pass
		return self.buffered
		
	def __call__( self, t ):
		if self.t0 is None: self.t0 = t
		t -= self.t0
		if t == self.t_prev: return self.f_prev
		self.t_prev = t
		
		if self.buffered: nextT, nextPiece = self.buffered[ 0 ]
		else: nextT = nextPiece = None
		isLastPiece = False
		value = None
		gotValue = False
		while nextT is None or nextT <= t or nextPiece is STITCH:
			if nextT is None and callable( self.currentPiece ):
				try:
					value = self.currentPiece( t )
				except StopIteration as exc:
					if nextPiece is not STITCH: self.buffered.insert( 0, ( t, exc.args[ -1 ] ) )
				else:
					gotValue = True
					break
			if self.buffered: _, self.currentPiece = self.buffered.pop( 0 )
			if not self.Buffer(): isLastPiece = True; break
			if nextT is None and nextPiece is not STITCH: break
			nextT, nextPiece = self.buffered[ 0 ]
		if not gotValue: value = self.currentPiece
		raiseIt = False
		if callable( value ):
			try:
				value = value( t )
			except StopIteration as exc:
				if len( exc.args ) != 1 or isinstance( exc.args[ -1 ], dict ):
					raise exc
				else:
					value = exc.args[ -1 ]
					self.currentPiece = value
					if isLastPiece: raiseIt = True
		elif isLastPiece:
			raiseIt = True
		if value is STITCH: value = None
		self.f_prev = value
		if raiseIt: raise Stop( value )
		return value

Unspecified = Constant( 'Unspecified' )
class StateMachine( object ):
	"""
	This class encapsulates a discrete-time state machine. Instances of
	this class are callable, with a single argument `t` for time.
	
	You can call a `StateMachine` instance multiple times with the same
	value of `t`.  Its logic will only run when `t` increases.

	Example::	
	
			sm = StateMachine()
			def PrintName( state ):
				print( state.name )
			sm.AddState( 'First', next='Second', duration=1.0, onset=PrintName )
			sm.AddState( 'Second', next='First', duration=2.0, onset=PrintName )
	
			import time
			while True:
				time.sleep( 0.1 )
				sm( time.time() )
	
	The magic of a `StateMachine` depends on how the states are defined.
	This can be done in a number of ways, the most powerful of which is
	to define each state as a subclass of `StateMachine.State`.
	
	See the `.AddState()` method for more details.
	"""
		
	NEXT = Constant( 'StateMachine.NEXT' )
	PENDING = Constant( 'StateMachine.PENDING' )
	CANCEL = Constant( 'StateMachine.CANCEL' )
	
	class State( object ):
		
		next = Unspecified
		duration = None
		onset = None
		offset = None
		__machine = None
		__name = None
			
		def __init__( self, name=None, duration=None, next=Unspecified, onset=None, ongoing=None, offset=None, machine=None ):
			if name     is not None: self.__name = name
			if machine  is not None: self.__machine = weakref.ref( machine )
			self.__set( duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset )
		
		def __set( self, **kwargs ):
			for attrName, value in kwargs.items():
				if value is Unspecified: continue
				if value is None and attrName != 'next': continue
				if callable( value ):
					try: inspect.getfullargspec
					except: args = inspect.getargspec( value ).args
					else:   args = inspect.getfullargspec( value ).args
					if len( args ): # this lets you set callables with either zero arguments or one argument (self) 
						if not hasattr( value, '__self__' ): value = value.__get__( self )
						if value.__self__ is not self and isinstance( value.__self__, StateMachine.State ): value = value.__func__.__get__( self )
				setattr( self, attrName, value )
		name                 = property( lambda self: self.__name if self.__name else self.__class__.__name__ )
		machine              = property( lambda self: self.__machine() )
		elapsed              = property( lambda self: self.__machine().elapsed_current )
		t                    = property( lambda self: self.__machine().t )
		fresh                = property( lambda self: self.__machine().fresh )
		Change = ChangeState = property( lambda self: self.__machine().ChangeState )
		
		def Elapsed( self, t=None ):
			"""
			Return the amount of time elapsed at time `t`, as measured from the
			most recent state change.
		
			If `t` is `None`, then the method returns the time elapsed at the most
			recent call to the `StateMachine`, a result that can also be obtained
			from the special property `self.elapsed`.
			"""
			return self.__machine().Elapsed( t, origin='current' )
		
		def __eq__( self, other ):
			if isinstance( other, str ): return self.name.lower() == other.lower()
			else: return self is other
				
	def __init__( self, *states ):
		self.__states = {}
		self.__current = None
		self.__current_duration = Unspecified
		self.__first_call_time = None
		self.__call_time = None
		self.__change_time = None
		self.__change_call_time = None
		self.__change_pending = []
		self.__last_added_state = None
		for arg in states:
			for state in ( arg if isinstance( arg, ( tuple, list ) ) else [ arg ] ):
				self.AddState( state )
			
	def AddState( self, state, duration=None, next=Unspecified, onset=None, ongoing=None, offset=None ):
		"""
		Add a new state definition to a `StateMachine`.
		
		Args:
			
			state
				This can be a string, defining the name of a new state.  Or it can be
				a class that inherits from `StateMachine.State`. Or it can be an actual
				instance of such a `StateMachine.State` subclass.
			
			duration
				A numeric constant, or `None`, or a callable that returns either a
				numeric constant or `None`. Determines the default duration of the
				state (`None` means indefinite).
			
			next
				A string, or a callable that returns a string, specifying the state
				to change to when the duration elapses, or when `.ChangeState()` is
				called without specifying a destination.  May also be `None` because
				`None` is a legal state for a `StateMachine` to be in.  Or it can
				be left entirely `Unspecified` in which case it means "the next state,
				if any, that I add to this `StateMachine` with `.AddState()`".
				
			onset
				Either `None`, or a callable routine that will get called whenever
				we enter this state.
			
			ongoing
				Either `None`, or a callable routine that will get called whenever the
				`StateMachine` is called and we are currently in the state.  If the
				callable `ongoing()` returns a string, the state machine will
				immediately attempt to change to the state named by that string.
			
			offset
				Either `None`, or a callable routine that will get called whenever
				we leave this state.
		
		`duration`, `next`, `onset`, `ongoing`, `offset` may be constants, callables
		that take no arguments, or callables that take one argument.  If they accept
		an argument, that argument will be an instance of `StateMachine.State`. This
		means they are effectively methods of your `State`, and indeed can be defined
		that way if you prefer.
		
		Since it is legal for the `state` argument to be a class definition, and for
		all the other arguments to be defined as attributes or methods of that class
		(instead of as arguments to this method),  one valid way to use the `.AddState`
		method is as a class decorator::
		
			import random
			
			sm = StateMachine()
			
			@sm.AddState
			class First( StateMachine.State ):
				next = 'Second'
				duration = 1.0
				def onset( self ):
					print( self.name )
				
			@sm.AddState
			class Second( StateMachine.State ):
				next = 'First'
				def onset( self ):
					print( self.name )
				def duration( self ):
					return random.uniform( 1, 5 )
				def ongoing( self ):
					if self.elapsed > 3.0:
						print( 'we apologize for the delay...' )
		
		Equivalently, you also can do::
		
			class First( StateMachine.State ):
				...
			class Second( StateMachine.State ):
				...	
			sm = StateMachine( First, Second )
		
		Equivalent state-machines can be defined without using the object-oriented
		class-definition approach: the syntax is simpler for very simple cases,
		but quickly explodes in complexity for more sophisticated machines. Here
		is an example, simplified relative to the above::
		
			sm = StateMachine()
			def PrintName( state ):
				print( state.name )
			sm.AddState( 'First', next='Second', duration=1.0, onset=PrintName )
			sm.AddState( 'Second', next='First', duration=2.0, onset=PrintName )
		
		"""
		if isinstance( state, ( type, StateMachine.State ) ):
			state = state() if isinstance( state, type ) else state 
			if not isinstance( state, StateMachine.State ): raise TypeError( 'if you use classes to define your states, they must be subclasses of StateMachine.State' )
			StateMachine.State.__init__( state, name=None, duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset, machine=self )
		else: state = StateMachine.State( name=state,      duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset, machine=self )
		if not self.__states: self.ChangeState( state.name )
		self.__states[ state.name ] = state
		if self.__last_added_state and getattr( self.__last_added_state, 'next', Unspecified ) is Unspecified:
			self.__last_added_state.next = state.name
		self.__last_added_state = state
		return state
	
	def ChangeState( self, newState=NEXT, timeOfChange=PENDING ):
		"""
		This method manually requests a change of state, the
		next time the `StateMachine` is called with a new
		time `t` value.
		
		Args:
		
			newState (str)
				If omitted, change to the state dictated by the
				current state's `.next` attribute/method.
				Otherwise, attempt to change to the state named
				by this argument.
			
			timeOfChange (float)
				This is used internally. To ensure accuracy,
				you should not specify this yourself. When called
				from outside the stack of an ongoing `StateMachine`
				call, this method actually only *requests* a state
				change, and the change itself will happen on, and be
				timed according to, the next occasion on which the
				the `StateMachine` instance is called with a novel
				time `t` argument.
		
		"""
		if newState is StateMachine.NEXT:
			newState = getattr( self.__current, 'next', None )
			if newState is Unspecified: newState = None
		if timeOfChange is StateMachine.PENDING:
			self.__change_pending.append( newState )
			return StateMachine.PENDING
		if callable( newState ):
			newState = newState()
		if isinstance( newState, StateMachine.State ):
			newState = newState.name
		if newState is StateMachine.CANCEL:
			return StateMachine.CANCEL
		if newState is Unspecified: newState = None
		if newState is not None:
			newState = self.__states[ newState ]
		offset = getattr( self.__current, 'offset', None )
		if callable( offset ): offset()
		if not( self.__current is None and newState is None ):
			if timeOfChange is None: timeOfChange = self.__call_time
			self.__change_time = timeOfChange
			self.__change_call_time = self.__call_time
		self.__current_duration = Unspecified
		self.__current = newState
		onset = getattr( self.__current, 'onset', None )
		if callable( onset ): onset()
		return newState
	
	t = property( lambda self: self.__call_time )
	state = current = property( lambda self: self.__current )	
	fresh = property( lambda self: self.__change_call_time == self.__call_time )
	
	elapsed_current = property( lambda self: None if ( self.__call_time is None or self.__change_time     is None ) else self.__call_time - self.__change_time )
	elapsed_total   = property( lambda self: None if ( self.__call_time is None or self.__first_call_time is None ) else self.__call_time - self.__first_call_time )

	def Elapsed( self, t=None, origin='total' ):
		"""
		Return the amount of time elapsed at time `t`, as measured either from
		the very first call to the `StateMachine` (`origin='total'`) or from the
		most recent state change (`origin='current'`).
		
		If `t` is `None`, then the method returns the time elapsed at the most
		recent call to the `StateMachine`, a result that can also be obtained from
		two special properties:
		
		* `self.elapsed_total`   same as  `self.Elapsed( t=None, origin='total' )
		* `self.elapsed_current` same as  `self.Elapsed( t=None, origin='current' )
		"""
		if origin == 'current': origin = self.__change_time
		elif origin == 'total': origin = self.__first_call_time
		if t is None: t = self.__call_time
		if origin is None or t is None: return None
		return t - origin
		
	def __call__( self, t ):
		if self.__call_time == t: return self.__current
			
		self.__call_time = t
		if self.__first_call_time is None:
			self.__first_call_time = self.__change_time = self.__change_call_time = t
		while self.__change_pending:
			self.ChangeState( newState=self.__change_pending.pop( 0 ), timeOfChange=t )
		
		# Note there's more than one way to change state - in descending order of recommendedness:
		# 
		# - you can rely on `state.duration` and `state.next`,
		# - or (for more dynamic behaviour) you can return a state name from `state.ongoing()`,
		# - or you can make an explicit call to `machine.ChangeState(...)` during your main loop,
		# - or you can make an explicit call to `self.Change(...)` during `state.ongoing()`, or
		#   even during `state.onset()` or `state.offset()` if you somehow absolutely must.
		# 
		# Note to maintainers: in principle you could *approximate* the function of .duration
		# and .next just by setting::
		# 
		#     ongoing = lambda self: 'SomeNewState' if self.elapsed >= someDuration else None
		# 
		# but do not imagine that .duration and .next are redundant: having them as explicit
		# attributes, and using the timeOfOrigin shuffle below, allows transitions to be
		# performed in such a way that quantization errors in state durations do not
		# accumulate over time:
		
		while True:
			
			duration = self.__current_duration
			if duration is Unspecified:
				duration = getattr( self.__current, 'duration', None )
				if callable( duration ): duration = duration()
				self.__current_duration = duration
				
			if duration is not None and self.elapsed_current is not None and self.elapsed_current >= duration:
				timeOfOrigin = self.__change_time
				if timeOfOrigin is None: timeOfOrigin = self.__first_call_time
				timeOfChange = timeOfOrigin + duration
				self.ChangeState( newState=getattr( self.__current, 'next', None ), timeOfChange=timeOfChange )
	
			ongoing = getattr( self.__current, 'ongoing', None )
			if not callable( ongoing ): break
			newState = ongoing()
			if not newState: break
			if self.ChangeState( newState=newState, timeOfChange=t ) is StateMachine.CANCEL: break
			
		return self.__current

def StateMachineDemo():
	sm = StateMachine()
	sm.AddState( 'first',  duration=123, next='second' )
	sm.AddState( 'second', duration=234, next='third' )
	sm.AddState( 'third',  duration=345, next='first' )
	import numpy; print( numpy.cumsum( [ 123, 234, 345, 123, 234, 345 ] ) )
	for t in range( 0, 1000, 2 ):
		state = sm( t )
		state = sm( t ) # it doesn't matter how many times the machine is queried with
		                # the same t: the change happens only once, and "fresh"-ness
		                # of the state persists until called with a different t
		if state.fresh:
			if state == 'first': print( 'passing GO, collecting $200' )
			print( '%5g: %s (elapsed = %r)' % ( t, state.name, state.elapsed ) )

if __name__ == '__main__':
	p = Apply( numpy.sin, Integral( Integral( 0.05 ) ) + [ numpy.pi / 2, 0] ) * 500
	
	print( p )
	print( p(0) )
	print( p(1) )
	print( p(2) )

