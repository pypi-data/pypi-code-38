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
	'BackEnd',
	'ReportVersions',
	'Screens',
	'CloseAllWorlds',
	'World',
	'Stimulus',
	'LookupTable',
	'IsShadyObject',
	'AddCustomSignalFunction',
	'AddCustomModulationFunction',
	'AddCustomWindowingFunction',
	'LoadImage',
	'Require', 'RequireShadyVersion',
	
	# constants
	'SIGFUNC', 'MODFUNC', 'WINFUNC', 'PRESCREENING', 'POSTPROCESSING', # enum-like namespaces
	'DRAWMODE',
	'LOCATION',
]

# Python standard library modules
import os
import re
import sys
import ast
import time
import glob
import math
import ctypes
import inspect
import weakref
import warnings
import textwrap
import functools
import threading
import traceback
import collections

# sibling sub-module imports
from . import Timing
from . import Logging
from . import PyEngine
from . import Location; from .Location import PackagePath
from . import PropertyManagement; from .PropertyManagement import ClassWithManagedProperties, ManagedProperty, ManagedShortcut
from . import DependencyManagement; from .DependencyManagement import Require, RequireShadyVersion
from . import Linearization; from .Linearization import LoadLUT

# global defs
MAX_TEXTURE_EXTENT = 8192 # TODO: found this empirically to be 16284 on Surface Pro and 8192 on MacBook; how to query it properly?   GL.glGetIntegerv( MAX_TEXTURE_SIZE )?
MAX_POINTS = 20000

class LOCATION( object ):
	"""
	This class is an enum container: a namespace of relative `(x,y)` tuples
	that can be assigned to the `.anchor` property of a `Stimulus` or `World`
	instance, or used as an argument to the `.Place()` method.
	"""
	BOTTOM_LEFT  = LOWER_LEFT   = ( -1, -1 )
	BOTTOM       = LOWER_CENTER = (  0, -1 )
	BOTTOM_RIGHT = LOWER_RIGHT  = ( +1, -1 )
	LEFT         = CENTER_LEFT  = ( -1,  0 )
	CENTER                      = (  0,  0 )
	RIGHT        = CENTER_RIGHT = ( +1,  0 )
	TOP_LEFT     = UPPER_LEFT   = ( -1, +1 )
	TOP          = UPPER_CENTER = (  0, +1 )
	TOP_RIGHT    = UPPER_RIGHT  = ( +1, +1 )

for name, value in LOCATION.__dict__.items():
	if not name.startswith( '_' ): __all__.append( name ); globals()[ name ] = value

class SIGFUNC( object ):
	"""
	This class is an enum container: a namespace of values that can be
	assigned to the `.signalFunction` property of a `Stimulus` instance.
	Its members are named according to the signal functions available in
	the shader. The only built-in function is `SinewaveSignal` which has
	a value of 1. So, when you set the `.signalFunction` property of a
	`Stimulus`  to 1, the `SinewaveSignal` function is selected in the
	shader, and when you set it to 0, no signal function is selected.
	
	You can define further signal functions, and hence add names and
	values to this namespace, with `AddCustomSignalFunction`.
	
	See also:  `MODFUNC`, `WINFUNC`
	"""
	NoSignal = 0
	SinewaveSignal = 1
class MODFUNC( object ):
	"""
	This class is an enum container: a namespace of values that can be
	assigned to the `.modulationFunction` property of a `Stimulus` instance.
	Its members are named according to the modulation functions available
	in the shader. The only built-in function is `SinewaveModulation` which
	has a value of 1. So, when you set the `.modulationFunction` property of
	a `Stimulus`  to 1, the `SinewaveModulation` function is selected in the
	shader, and when you set it to 0, no modulation function is selected.
	
	You can define further modulation functions, and hence add names and
	values to this namespace, with `AddCustomModulationFunction`.
	
	See also:  `SIGFUNC`, `WINFUNC`
	"""
	NoModulation = 0
	SinewaveModulation = 1
class WINFUNC( object ):
	"""
	This class is an enum container: a namespace of values that can be
	assigned to the `.windowingFunction` property of a `Stimulus` instance.
	Its members are named according to the windowing functions available in
	the shader. The only built-in function is `Hann` which has a value of 1.
	So, when you set the `.windowingFunction` property of a `Stimulus` to
	1, the `Hann` function is selected in the shader, and when you set it
	to 0, no windowing function is selected.
	
	You can define further windowing functions, and hence add names and
	values to this namespace, with `AddCustomWindowingFunction`.
	
	See also:  `SIGFUNC`, `MODFUNC`
	"""
	NoWindowing = 0
	Hann = 1

def enum( val, doc ):
	class enum( int ): __doc__ = doc
	return enum( val )
	
class DRAWMODE( object ):
	"""
	This class is an enum container: a namespace of values that can be
	assigned to the `.drawMode` property of a `Stimulus` instance. The
	default `.drawMode` is `DRAWMODE.QUAD`:  that means that each
	`Stimulus` is automatically drawn as a rectangle according to its
	`.envelopeSize`.
	
	Other modes rely on the `.points` property, which contains a
	sequence of two-dimensional coordinates:
	
		* `DRAWMODE.POINTS` draws a disconnected dot at each location.
		* `DRAWMODE.LINES` takes two locations at a time and connects
		  each pair with a line segment, disconnected from previous or
		  subsequent line segments.
		* `DRAWMODE.LINE_STRIP` draws line segments continuously from
		  one location to the next, only taking the pen off the paper
		  if it enounters a NaN coordinate.
		* `DRAWMODE.LINE_LOOP` is like LINE_STRIP, but the last point
		  in each group is joined back to the first (where a "group"
		  is delimited by NaNs in the sequence of coordinates).
		* `DRAWMODE.POLYGON` also connects successive locations
		  continuously, and fills the area bounded by the lines thus
		  drawn (a NaN coordinate is a way to delimit multiple
		  polygons)	
	"""
	QUAD       = enum( 1, "Draw a rectangle according to `.envelopeSize`, ignoring `.points`")
	POINTS     = enum( 2, "Draw disconnected points at the locations in `.points`" )
	LINES      = enum( 3, "Draw disjoint line segments joining each successive pair of locations in `.points`" )
	LINE_STRIP = enum( 4, "Draw connected line segments from one location to the next in `.points`, breaking only for NaNs" )
	POLYGON    = enum( 5, "Draw filled polygons with vertices specified by `.points`, closing each polygon and beginning a new one when a NaN is encountered" )
	LINE_LOOP  = enum( 6, "Draw connected line loops from one location to the next in `.points`, closing each loop when a NaN is encountered" )

# home-made 'six'-esque stuff:
try: FileNotFoundError
except NameError: FileNotFoundError = IOError
if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x
def reraise( cls, instance, tb=None ): raise ( cls() if instance is None else instance ).with_traceback( tb )
try: Exception().with_traceback
except: exec( 'def reraise( cls, instance, tb=None ): raise cls, instance, tb' ) # has to be wrapped in exec because this would be a syntax error in Python 3.0
class DeferredException( object ):
	def __init__( self, cls, instance, tb=None ): self.cls, self.instance, self.tb = cls, instance, tb
	def __call__( self ): reraise( self.cls, self.instance, self.tb )

# basic tools
call = lambda x: x()
IDENTITY3FV = ( 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0 )
IDENTITY4FV = ( 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0 )

__meta__ = ast.literal_eval( open( PackagePath( 'MASTER_META' ), 'rt' ).read() )
__version__ = __meta__[ 'version' ]
DependencyManagement.RegisterVersion( name='Shady', value=( __version__, Logging.GetRevision(), PackagePath( '.' ) ) )

# third-party package imports
from . import Dependencies; from .Dependencies import numpy, Image, ImageGrab

_windowing_backend_requested = None
_windowing_backend_loaded = None
_acceleration_preference = 'auto-silent'
Windowing = None
ShaDyLib = None

def Announce( msg, wrapWidth=None, file=None ):
	if file is None: file = sys.stderr
	msg = '%s\n' % msg
	if wrapWidth: 
		stripped = msg.lstrip( '\n' ); before = msg[ :len( msg ) - len( stripped ) ]
		stripped = msg.rstrip( '\n' ); after  = msg[ len( stripped ): ]
		msg = before + '\n'.join( textwrap.wrap( msg, wrapWidth ) ) + after
	file.write( msg )
	try: file.flush()
	except: pass


def PrintStack( limit=None ):
	try:
		frame = inspect.currentframe()
		outerframes = inspect.getouterframes( frame )
		traceback.print_stack( outerframes[ 2 ][ 0 ], limit=limit )
		print( '' )
	finally:
		del outerframes, frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack

# C++ acceleration
def LoadAccelerator( preference=None ):
	"""
	See `BackEnd()`.
	"""
	global ShaDyLib
	if preference in [ True ] and ShaDyLib is not None: return ShaDyLib  
	develDir = PackagePath( '../../accel-src/release' )
	develLoaded = ShaDyLib is not None and inspect.getfile( ShaDyLib ).startswith( develDir )
	bundledLoaded = ShaDyLib is not None and not develLoaded
	if preference in [ False ] or ( preference in [ 'bundled' ] and not bundledLoaded ) or ( preference in [ 'devel' ] and not develLoaded ):
		ShaDyLib = None
		sys.modules.pop( 'ShaDyLib', None )
		sys.modules.pop( 'Shady.ShaDyLib', None )
		if develDir in sys.path: sys.path.remove( develDir )
		# Tabula rasa in theory but note that this can cause strange bugs where module members become None when imported a second time (at least on OSX under anaconda 2.7.12 - also reported in a comment by Olivier Verdier at https://stackoverflow.com/a/2918951/ )
	if preference in [ 'devel', 'auto', 'auto-silent', True ]:
		if os.path.isdir( develDir ):
			sys.path.insert( 0, develDir )
			try: import ShaDyLib
			except ImportError: pass
			sys.path.remove( develDir )
		if ShaDyLib:
			if preference in [ 'auto', True ]: Announce( 'Shady accelerated using development library %r' % ShaDyLib.dll._name )
			return ShaDyLib
		if preference in [ 'devel' ]: raise ImportError( 'failed to import development version of ShaDyLib accelerator' )
	if preference in [ 'bundled', 'auto', 'auto-silent', True ]:
		try: from . import accel; from .accel import ShaDyLib
		except ImportError:
			if preference in [ 'bundled' ]: raise ImportError( 'failed to import bundled version of ShaDyLib accelerator' )
		if ShaDyLib:
			if preference in [ 'auto', True ]: Announce( 'Shady accelerated using bundled library %r' % ShaDyLib.dll._name )
			return ShaDyLib
	elif preference not in [ None, False ]:
		raise ValueError( 'unrecognized accelerator preference %r' % preference )
	if not ShaDyLib:
		if preference in [ True ]: raise ImportError( 'failed to import ShaDyLib accelerator' )
		if preference in [ 'auto' ]: Announce( 'Shady is running without acceleration' )
	return ShaDyLib

def BackEnd( windowing=None, acceleration=None ):
	"""
	Globally specify the back-end windowing and rendering systems that future
	`World` instances should use.
	
	Args:
	    windowing:
	        specifies the windowing system. Possible values are as follows:
	    
	        `'default'`:
	              use the ShaDyLib dynamic library if available, else fall back
	              on pyglet.
	        `'shadylib'`, `'accel'`, or `'glfw'`:
	              use the ShaDyLib dynamic library (windowing is handled via the
	              GLFW library from http://glfw.org ).
	        `'pyglet'`:
	              use pyglet (a third-party package that you will need
	              to install separately if you want to use this option)
	        `'pygame'`:
	              use pygame (a third-party package that you will need
	              to install separately if you want to use this option)
	    
	    acceleration:
	        specifies the rendering implementation, i.e. whether to use the ShaDyLib
	        dynamic library (and if so, whether to use the "development" copy of
	        ShaDyLib in cases where you have the entire Shady repository including
	        the C++ sources for ShaDyLib) or whether to fall back on Python code
	        for rendering (not recommended). Possible values are:

	        `None`:
	              leave things as they were (default).
	        `False`:
	              disable ShaDyLib and fall back on the `pyglet` or `PyOpenGL`
	              code in the `PyEngine` submodule (this option is not
	              recommended for time-critical presentation).
	        `True`:
	              if ShaDyLib is already imported, leave things as they are;
	              if not, import either version of ShaDyLib or die trying.
	              Prefer the development version, if available. Print the
	              outcome.
	        `'bundled'`:
	              silently import the bundled version of ShaDyLib from the
	              Shady.accel sub-package, or die trying.
	        `'devel'`:
	              silently import the development version of ShaDyLib from
	              `../../accel-src/release/`, or die trying.
	        `'auto'`:
	              try to import ShaDyLib. Prefer the development version,
	              if available. Don't die in the attempt. Whatever happens,
	              print the outcome.
	
	Returns:
	    If both input arguments are `None`, the name of the current windowing back-end
	    is returned. Otherwise, returns `None`.
	"""
	global _windowing_backend_requested, _acceleration_preference
	if windowing is None and acceleration is None: return _windowing_backend_requested
	if windowing is None: windowing = _windowing_backend_requested
	if windowing is not None:
		windowing = windowing.lower()
		if windowing.endswith( 'windowing' ): windowing = windowing[ :-9 ]
		if windowing == 'default': windowing = 'shadylib'
		if windowing in [ 'accel', 'shadylib', 'glfw' ]:
			if acceleration == False: raise ValueError( 'cannot set acceleration=False if using %r back-end for windowing' % windowing )
			if acceleration is None: acceleration = _acceleration_preference
			if acceleration is None: acceleration = True
			windowing = 'shadylib'
		_windowing_backend_requested  = windowing
	if acceleration is not None:
		_acceleration_preference = acceleration
	
def LoadBackEnd():
	# Load (import) the active windowing backend as configured by `BackEnd()`.
	global Windowing, _windowing_backend_loaded
	if _windowing_backend_requested is None: BackEnd( 'default', _acceleration_preference )
	LoadAccelerator( _acceleration_preference )
	if _windowing_backend_requested == 'shadylib' and not ShaDyLib: raise ImportError( 'failed to import ShaDyLib accelerator, which is required when using the "shadylib" windowing option' )
	if _windowing_backend_requested == _windowing_backend_loaded: return Windowing
	elif _windowing_backend_requested == 'pyglet':   from . import PygletWindowing   as Windowing
	elif _windowing_backend_requested == 'pygame':   from . import PygameWindowing   as Windowing
	elif _windowing_backend_requested == 'shadylib': from . import ShaDyLibWindowing as Windowing  # NB: requires accelerator to be loaded here
	else: raise ValueError( 'unsupported back-end module %r' % _windowing_backend_requested )
	_windowing_backend_loaded = _windowing_backend_requested
	Windowing.Window.TabulaRasa()
	return Windowing

def Screens( pretty_print=False ):
	"""
	Get details of any attached screens using the `Screens()` method
	of whichever windowing backend is enabled.
	
	Args:
		pretty_print (bool): determines the type of the return value
	
	Returns:
		If `pretty_print` is `True`, returns a human-readable string.
		If `pretty_print` is `False`, returns a `dict`.
	"""
	LoadBackEnd()
	hijacker = getattr( World, '_thread_hijacker', None )
	if hijacker: return hijacker.WaitFor( Windowing.Screens, pretty_print=pretty_print )
	else: return Windowing.Screens( pretty_print=pretty_print )

def ReportVersions( world=None, outputType='print', importAll=False ):
	"""
	Report versions of all dependencies, including:
	
		* the windowing backend (pyglet, pygame, or ShaDyLib)
		* the acceleration backend (ShaDyLib)
		* any other dependencies managed by Shady, such as `numpy`.
	
	Args:
	    world (World):
	    	optional `Shady.World` instance (if supplied, more
	    	information can be provided).
	    outputType (str):
	    	may be `'dict'`, `'string'` or `'print'`
	
	Returns:
	    Depending on `outputType`, may return a `dict` or a string
	    detailing Shady's various subcomponents and dependencies and 
	    their version information.
	"""
	LoadBackEnd()
	if importAll: DependencyManagement.ImportAll()
	versions = DependencyManagement.GetVersions()
	versions[ 'backend' ] = _windowing_backend_loaded
	if world:
		versions[ 'backend' ] = world.backend
		versions.update( getattr( world.window, 'versions', {} ) )
		versions.update( getattr( world._accel, 'versions', {} ) )
	global ShaDyLib
	if ShaDyLib:
		accel = ShaDyLib.dll._name.replace( '\\', '/' )
		root = PackagePath( '..' ).replace( '\\', '/' ).rstrip( '/' ) + '/'
		if accel.startswith( root ): accel = accel[ len( root ): ]
		if world is None or 'ShaDyLib' in versions: # yes, that is what I mean
			versions[ 'ShaDyLib' ] = ( ShaDyLib.GetVersion(), ShaDyLib.GetRevision(), ShaDyLib.GetCompilationDatestamp(), accel )
	if outputType in [ 'dict', dict ]: return versions
	s = '\n'.join( '%30r : %r,' % item for item in versions.items() )
	if outputType in [ 'str', 'string', str ]: return s
	elif outputType == 'print': print( '\n' + s + '\n' )
	else: raise ValueError( 'unrecognized output type %r' % outputType )

_SPHINXDOC = any( os.environ.get( varName, '' ).lower() not in [ '', '0', 'false' ] for varName in [ 'SPHINX' ] )

def DeferredCall( func, context=None ):
	if _SPHINXDOC: return func
	@functools.wraps( func )
	def deferred( *pargs, **kwargs ):
		world = context
		if world is None:
			self = pargs[ 0 ]
			world = getattr( self, 'world', self )
		if callable( world ): world = world() # weakref de-ref
		if world._parentThread in [ None, threading.current_thread() ]:
			return func( *pargs, **kwargs )
		container = world.Defer( func, *pargs, **kwargs )
		while not container and world.state not in [ 'finished', 'closed' ]: time.sleep( 0.001 )
		result = container[ 0 ] if container else None
		if isinstance( result, DeferredException ): result()
		return result
	return deferred
			
def ExceptionHook( name, exc, tb ):	
	hook = sys.excepthook
	if 'IPython' in sys.modules:
		# Wrestle with the IPython devs, goalpost-movers extraordinaires:
		try: from IPython.core.ultratb import ColorTB
		except ImportError: pass
		else: hook = ColorTB()
		try: from IPython.ultraTB import ColorTB
		except ImportError: pass
		else: hook = ColorTB()
		try: hook.ostream = sys.stderr
		except: pass
		
	stem = PackagePath( '.' )
	extracted = list( traceback.extract_tb( tb ) )
	first_of_interest = 1 + max( [ i for i, f in enumerate( extracted ) if f[ 0 ].startswith( stem ) ] + [ -1 ] )
	if first_of_interest < len( extracted ):
		for i in range( first_of_interest ): tb = tb.tb_next
	hook( name, exc, tb )
	try: sys.stderr.flush()
	except: pass

def PartialTranslation( v, p ):
	return math.floor( ( 0.5 + 0.5 * p ) * v )

def StimulusSortKey( stim ):
	return ( -getattr( stim, 'z', 0 ) - getattr( stim, 'oz', 0 ), getattr( stim, 'serialNumber', 0 ) )

class ProfileContextManager( object ):
	def __init__( self, enabled=False, mode=True, report_streams=() ):
		self.nFrames = 0
		self.mode = mode
		self.enabled = enabled
		self._depth = 0
		self.__text_pending = ''
		self.__report_streams = report_streams
		if self.mode == 'pyinstrument':
			pyinstrument = DependencyManagement.Import( 'pyinstrument' )
			self.profile = pyinstrument.Profiler( use_signal=not sys.platform.lower().startswith( 'win' ) )
		elif self.mode == 'hotshot':
			import hotshot
			self.tempfile = 'hotshot.bin' # TODO
			self.profile = hotshot.Profile( self.tempfile, 1, 1 )
		#elif self.mode == 'profile':
		#	import profile
		#	self.profile = profile.Profile()   # fails - see https://stackoverflow.com/questions/52998945
		elif self.mode == 'cProfile' or self.mode == True:
			import cProfile
			self.profile = cProfile.Profile()
		else:
			self.profile = None
		self.running = self.ChildCM( self )
	class ChildCM( object ):
		def __init__( self, parent ):
			self.parent = weakref.ref( parent )
		def __enter__( self ):
			parent = self.parent()
			if not parent or not parent.profile or not parent.enabled: return parent
			parent._depth += 1
			if parent._depth > 1: return parent
			if parent.mode in [ 'pyinstrument', 'hotshot' ]: parent.profile.start()
			else: parent.profile.enable()
			return parent
		def __exit__( self, etype, einst, tb ):
			parent = self.parent()
			if not parent or not parent.profile or parent._depth < 1: return
			parent._depth -= 1
			if parent._depth: return
			if parent.mode in [ 'pyinstrument', 'hotshot' ]: parent.profile.stop()
			else: parent.profile.disable()
			parent.nFrames += 1
	def __enter__( self ):
		self.enabled = True
	def __exit__( self, etype, einst, tb ):
		self.enabled = False
	def enable( self ):
		self.enabled = True
		return self
	def disable( self ):
		self.enabled = False
		return self
	def write( self, txt ):
		streams = self.__report_streams if self.__report_streams else [ sys.stdout ]
		for line in txt.splitlines( True ):
			self.__text_pending += line
			if self.__text_pending.endswith( '\n' ):
				line, self.__text_pending = self.__text_pending, ''
				for out in streams:
					if hasattr( out, 'write' ): out.write( line )
					else: out( line.rstrip( '\n' ) )
	def stats( self ):
		class NoStats( object ):
			def __init__( self, msg ): self.msg = msg
			def __bool__( self ): return False
			def __nonzero__( self ): return False
			def __repr__( self ): return 'no profile statistics available - ' + self.msg
			def print_stats( self, *p, **kw ): print( self )
		if not self.profile: return NoStats( 'profiler was not created' )
		if not self.nFrames: return NoStats( 'no frames were measured' )
		if self.mode == 'pyinstrument':
			def MsecPerFrame( f ):
				if hasattr( f, '_time' ): del f._time
				if not hasattr( f, '_total_self_time' ): f._total_self_time = f.self_time
				f.self_time = f._total_self_time * 1000.0 / self.nFrames
				for child in f.children: MsecPerFrame( child )
			MsecPerFrame( self.profile.starting_frame() )
			if self.__report_streams: warnings.warn( 'pyinstrument profiler reports will not be included in the log file by default' ) # TODO
			return self.profile
		elif self.mode == 'hotshot':
			import hotshot.stats
			p = hotshot.stats.load( self.tempfile ).sort_stats( 'cumtime' )
			# TODO: empty
			# TODO: normalize stats to msec per frame somehow...?
			if self.__report_streams: warnings.warn( 'hotshot profiler reports will not be included in the log file by default' ) # TODO
			return p
		else:
			import pstats
			p = pstats.Stats( self.profile ).sort_stats( 'cumtime' ) 
			# TODO: normalize stats to msec per frame somehow...?
			p.stream = self
			return p
	def __del__( self ):
		if self.__text_pending: self.write( '\n' )
def IsShadyObject( obj ):
	return bool( getattr( obj, '_isShadyObject', False ) )

ATMOSPHERE_PROPERTIES = 'backgroundColor noiseAmplitude gamma ditheringDenominator lookupTableTextureSize lookupTableTextureSlotNumber lookupTableTextureID'.split()

@ClassWithManagedProperties._Organize
class LinkGL( ClassWithManagedProperties ):
	"""
	Superclass for the `World`, `Stimulus` and `LookupTable` classes, whose principal
	function is to allow easy transfer of 1-, 2-, 3- or 4-dimensional OpenGL parameters.	
	"""
	
	_isShadyObject = True
		
	def _Initialize( self, world, debugTiming=False ):
		self.world = weakref.ref( world )
		if debugTiming is None: debugTiming = getattr( world, 'debugTiming', False )
		self.debugTiming = debugTiming
		self._verbose = 0
		self._excepthook = ExceptionHook
		self._scheduled = {}
		if not self._accel: PyEngine.SetUpProperties( self, world=world ) # copies default values into place, AND sets up transfers
	
	def _Accelerate( self, accel, **preserve ): 
		if not accel: return None
		preserve = { k : v * 1 for k, v in preserve.items() }
		if hasattr( accel, 'MakeCustomUniform' ):
			for prop in getattr( self, '_custom_properties', [] ):
				accel.MakeCustomUniform( prop.name, int( prop.transfer[ -2 ] ), prop.transfer[ -1 ] == 'f' )
				preserve[ prop.name ] = getattr( self, prop.name )
		for prop in self.Properties( False ):
			try: prop_accel = accel.GetProperty( prop.name )
			except: pass; Announce( 'failed to accelerate %s.%s' % ( self.__class__.__name__, prop.name ) )
			else:
				array = PropertyManagement.WrapPropertyArray( prop_accel.A, prop )
				prop.determine_array( self, array=array )#; Announce( 'accelerated %s.%s = %s' % ( self.__class__.__name__, prop.name, array ) )
				if not prop.default_changed and prop.name in [ 'clearColor', 'ditheringDenominator' ]:
					# these properties are special cases because the engine actually manipulates them
					# in a way that it is convenient to preserve as "default"
					# clearColor purely because it's so useful to colour-code the backend/acceleration status
					# ditheringDenominator because its one-and-only reasonable value (usually 255) is queried via OpenGL during InitShading
					prop.SetDefault( array )
				else:
					setattr( self, prop.name, prop.default )
		self.Set( **preserve )
		if hasattr( accel, 'SetUpdateCallback' ): # only Renderer objects will have this method
			self._accel_callback = ShaDyLib.UpdateCallback( self._FrameCallback )  # must assign this wrapped object as an attribute here, otherwise the garbage-collector will get it and the callback will cause a segfault when it happens
			accel.SetUpdateCallback( self._accel_callback, 0 )
		return accel

	def _RedirectProperty( self, propertyName, targetInstance, targetArray=None ):
		# overshadows superclass method ClassWithManagedProperties._RedirectProperty
		if not getattr( self, '_accel', None ): return ClassWithManagedProperties._RedirectProperty( self, propertyName=propertyName, targetInstance=targetInstance, targetArray=targetArray )
		# ...but only if there is a self._accel
		descriptor = self.GetPropertyDescriptor( propertyName )
		propertyName = descriptor.name
		p = self._accel.GetProperty( propertyName )
		if targetInstance is None or targetInstance is self: p.MakeIndependent( 0 )
		else: p.LinkWithMaster( targetInstance._accel.GetProperty( propertyName )._ptr )
		descriptor.determine_array( self, name=propertyName, array=p.A )
	
	def _Record( self, key, value=None, origin=0.0, factor=1.0, bufferSize=36000 ):
		if value is None: value = self.world()._Clock()
		if not hasattr( self, 'timings' ): self.timings = Bunch()
		array = self.timings.get( key, None )
		if array is None:
			if numpy: array = numpy.zeros( [ bufferSize ], dtype=float ) + numpy.nan
			else: array = [ float( 'nan' ) ] * bufferSize
			self.timings[ key ] = array
		array[ self.framesCompleted % len( array ) ] = ( value - origin ) * factor
		return value
		
	def _DebugTiming( self, key, timeInSeconds=None, origin=None ):
		world = self.world()
		if origin is None: origin = world._drawTime
		return world._Record( self._Description().replace( ' ', '_' ).replace( "'", '' ).replace( '"', '' ) + '_' + key, value=timeInSeconds, origin=origin, factor=1000.0 )
		
	def _Description( self ):
		desc = self.__class__.__name__
		name = getattr( self, 'name', '' )
		if name: desc += ' %r' % name
		return desc	
	
	def __str__( self ): return self._Description()
	def __repr__( self ): return '<%s @ 0x%08x>' % ( self._Description(), id( self ) )
		
	def _CallAnimate( self, t ):
		try:
			self.Animate( t )
		except:
			einfo = sys.exc_info()
			method = self.Animate
			self.SetAnimationCallback( None )
			if method:
				sys.stderr.write( 'Exception during .Animate() callback of %r:\n' % self )
				ExceptionHook( *einfo )
	
	def _BindCallable( self, name, func, numberOfArgsAfterSelf, container=None, slot=0 ):
		"""
		grok `func` to determine whether it's an already-bound method, or an unbound method/function
		with or without `self` in addition to the expected number of arguments. Bind it appropriately
		if there's room for `self`.  Then attach it as
		
		- a named attribute of `self`, if `container` is `None`
		- container[ slot ]  if `container` is provided
		"""
		if func == 'default' and name: func = getattr( type( self ), name, None )
		if func is None:
			if container is None: setattr( self, name, func )
			else: container.pop( slot, None )
			return self
		if inspect.isgeneratorfunction( func ):
			try: func = func( self )
			except: func = func()
		if inspect.isgenerator( func ):
			gen = func
			wr = weakref.ref( self )
			def func( _ ):
				try: return next( gen )
				except StopIteration: wr()._BindCallable( name=name, func=None, numberOfArgsAfterSelf=numberOfArgsAfterSelf, container=container, slot=slot )
		if hasattr( func, '__get__' ):
			try: inspect.getfullargspec
			except: args = inspect.getargspec( func ).args
			else:   args = inspect.getfullargspec( func ).args
			if len( args ) == numberOfArgsAfterSelf + 1:
				if not hasattr( func, '__self__' ): func = func.__get__( self, type( self ) )
				#if func.__self__ is not self: func = func.__func__.__get__( self, type( self ) )
			elif len( args ) != numberOfArgsAfterSelf:
				if not name: name = ''
				raise TypeError( '%r function should have either %d arguments (if the first is `self`) or %d (if omitting `self`)' % ( name, numberOfArgsAfterSelf + 1, numberOfArgsAfterSelf ) )
		if container is None: setattr( self, name, func )
		else: container[ slot ] = func
		return func
	
	Animate = None
		
	def SetAnimationCallback( self, callback ):
		"""
		Bind the callable object `callback` as the instance's animation
		callback. Each object, whether it is a `World` or a `Stimulus`, may
		optionally have a single animation callback which is called on every
		frame. If the `callback` argument is `None`, any existing callback is
		removed.
		
		The animation callback is installed as the attribute `self.Animate`.
		By default, this attribute is `None`.
		
		The prototype for an animation callback can be `callback(self, t)`
		or just `callback(t)` (if it's the latter then you can, alternatively,
		simply assign it as `self.Animate = callback` ).
		
		Example::
		
			def animate( self, t ): 
				print( t )
			my_world = Shady.World().SetAnimationCallback( animate )
		
		There is also a decorator version of the same operation, simply called
		`.AnimationCallback()`::
		
			stim = my_world.Stimulus()
			@stim.AnimationCallback
			def Animate( self, t ):
				print( t )
		"""
		self._BindCallable( 'Animate', callback, numberOfArgsAfterSelf=1 )
		return self
	
	def AnimationCallback( self, func=None ):
		"""
		Decorator version of `.SetAnimationCallback()`
		
		Examples::
		
			w = Shady.World()
			
			@w.AnimationCallback
			def anim( self, t ):
				print( t )
		
		"""
		if func is None: return lambda func: self.SetAnimationCallback( func ) and func
		else: return self.SetAnimationCallback( func ) and func
	
	def SetVerbosity( self, n, sleep=0.0, propagate=True ):
		self._verbose = n
		if not propagate: return
		if hasattr( self, 'stimuli' ):
			for stim in self.stimuli.values(): stim.SetVerbosity( n, sleep=0.0, propagate=True )
		if sleep: time.sleep( sleep )
	
	def WaitFor( self, condition ):
		"""
		This function blocks the current thread until a specified `condition`
		becomes `True`. The `condition` will be checked repeatedly in between
		1-millisecond sleeps. It can be one of two things:
		
		* a callable (function) which returns `True` to signal that the wait
		  is over - e.g.::
		      
		      stim.WaitFor( lambda: stim.y < 0 )
		
		* a string that names a dynamic attribute belonging to the current
		  instance. In this case, the wait ends when there is no longer a
		  dynamic attached the the property or shortcut in question. A
		  dynamic may be removed due to explicit action of another thread
		  in your program, or explicit action in this instance's
		  `AnimationCallback` (or indeed any instance's `AnimationCallback`).
		  Alternatively, a dynamic may automatically remove itself, by
		  raising a `StopIteration` exception (the `Function` object returned
		  by `Shady.Dynamics.Transition` is an example of something that
		  does this)::
		  
		      stim.scaling = Shady.Transition( stim.scaling, 2, duration=5 )
		      # the stimulus will now double in size over the course of 5 sec
		      stim.WaitFor( 'scaling' )
		      # wait until it's finished
		
		All of this assumes that you are operating in a different thread
		from the `World`---if you call `WaitFor` from inside one of the
		`World` or `Stimulus` callbacks, then it will simply sleep
		indefinitely because nothing will get the chance to change.
		"""
		if isinstance( condition, str ):
			propertyName = condition
			if propertyName == 'all': condition = lambda: not self.GetDynamics()
			else: condition = lambda: self.GetDynamic( propertyName ) is None
		if self.world()._parentThread in [ None, threading.current_thread() ]:
			#print( 'skipping WaitFor() because it has been called from the World thread...' )
			return self
		while not condition():
			time.sleep( 0.001 )
		return self
			
	def Place( self, xp, yp=None, worldCoordinates=True, polar=False ):
		"""
		Convert 2-D normalized coordinates (relative to the instance, -1 to +1 in each
		dimension), into 2-D pixel coordinates, either relative to the `World`'s current
		`.anchor`, or relative to the `World`'s bottom left corner irrespective of `.anchor`.
		
		Input coordinates may be given as one scalar argument,  two scalar arguments, or
		one argument that is a sequence of two numbers.  Depending on the `polar` argument,
		these will be interpreted as `x, y` Cartesian coordinates (where, if `y` omitted,
		it defaults to `y=x`)  or `theta, r` polar coordinates (where, if `r` is omitted,
		it defaults to `r=1`).
		
		Args:
		    worldCoordinates (bool):
		        If `True`, return pixel coordinates relative to the `World`'s own `.anchor`
		        position.  If `False`, return pixel coordinates relative to the `World`'s
		        bottom left corner irrespective of its `.anchor`.
		    
		    polar (bool):
		        If `True`, input coordinates are interpreted as an angle (in degrees) and
		        an optional radius (0 denoting the center, 1 denoting the edge).
		
		Examples::
		
		    instance.Place( [ -1, 1 ] )      # top left corner
		    instance.Place( -1, 1 )          # likewise, top left corner
		    instance.Place( 90, polar=True )  # middle of top edge (radius 1 assumed)
		    instance.Place( [ 90, 0.5 ], polar=True )  # halfway between center and top
		    instance.Place( 90, 0.5, polar=True )  # likewise, halfway between center and top
		
		"""
		( x0, y0 ), ( w, h ) = self.BoundingBox( worldCoordinates=worldCoordinates )
		if polar:
			theta, r = xp, yp
			if r is None:
				try: theta, r = theta
				except: r = 1.0
			theta *= math.pi / 180.0
			xp = r * math.cos( theta )
			yp = r * math.sin( theta )
		elif yp is None:
			try: xp, yp = xp
			except: yp = xp
		x = x0 + PartialTranslation( w, xp )
		y = y0 + PartialTranslation( h, yp )
		if numpy: return numpy.array( [ x, y ] )
		else: return [ x, y ]
		
	def ShareAtmosphere( self, *others ):
		return self.ShareProperties( ATMOSPHERE_PROPERTIES, *others )
	
	def LinkAtmosphereWithMaster( self, master ):
		return self.LinkPropertiesWithMaster( master, ATMOSPHERE_PROPERTIES )
	
	@call
	def atmosphere():
		doc = """
		This property actually encompasses multiple managed properties, all
		related to linearization and dynamic-range enhancement.
		
		If you query this property, you will get a `dict` of the relevant
		property names and values.  You can also assign such a dictionary to it.
		
		More usefully, you can use it to link all the properties between instances
		in one go::
		
			stim.atmosphere = world   # hard-links all the "atmosphere" properties
			                          # at once
		
		For more information, see the `Shady.Documentation.PreciseControlOfLuminance`
		docstring :doc:`or click here <../auto/PreciseControlOfLuminance>`.
		"""
		def fget( self ):
			return { k : getattr( self, k ) for k in ATMOSPHERE_PROPERTIES }
		def fset( self, value ):
			if isinstance( value, LinkGL ) and all( hasattr( value, name ) for name in ATMOSPHERE_PROPERTIES ):
				self.LinkAtmosphereWithMaster( value )
			else:
				self.Set( **value )
		return property( fget=fget, fset=fset, doc=doc )
	
	@call
	def lut():
		doc = """
		The value of this property will either be `None`, or an instance of `LookupTable`.
		Assigning to this property is equivalent to calling the `.SetLUT()` method---so
		you can assign any of the valid argument types accepted by that function.
		Assigning `None` disables look-up.
		"""
		def fget( self ):
			try: lut = self.__lut
			except: lut = None
			if lut is not None: return lut
			try: key = tuple( self.lookupTableTextureSize ) + ( self.lookupTableTextureSlotNumber, self.lookupTableTextureID )
			except AttributeError: return None
			ref = ALL_LOOKUPTABLES.get( key, None )
			return None if ref is None else ref()
		def fset( self, value ): self.SetLUT( value )
		return property( fget=fget, fset=fset, doc=doc )
		
	@DeferredCall
	def SetLUT( self, value ):
		"""
		Sets or unsets a `LookupTable` for a `World` or `Stimulus`. (For `World`s,
		this will only be effective to the extent that the `World`'s `atmosphere`
		properties are shared with `Stimulus` instances---for example, the canvas.)
		
		Calling this method is the functional equivalent of setting the `.lut`
		property::
		
			stim.SetLUT( value )  # These are equivalent
			stim.lut = value      # 
		
		Setting a look-up table disables automatic linearization via `.gamma` and
		automatic dynamic-range enhancement via `.ditheringDenominator`, and allows
		you to take direct control of these issues (although only for one dimension
		of luminance per pixel: using a look-up table is a form of indexed-color
		rendering).
		
		See the `Shady.Documentation.PreciseControlOfLuminance` docstring or 
		:doc:`../auto/PreciseControlOfLuminance` for more details.
		
		Args:
			value (None, str, list, numpy.ndarray, LookupTable):
				A pre-existing `LookupTable` instance may be used here. Alternatively,
				any valid constructor argument for a `LookupTable` may be used, and
				the instance will be constructed implicitly. That means you can use:
				
				- a `numpy.ndarray` of integers in `n`-by-3 or `m`-by-`n`-by-3
				  arrangement, or
				- a list of lists that can be implicitly converted into such an array
				  by `numpy`, or
				- the filename of a `.npy` or `.npz` file that contains such an array
				  (under the variable name `lut` in the latter case) to be loaded by
				  `Shady.Linearization.LoadLUT()`, or
				- the filename of a `.png` file containing the look-up table entries
				  as RGB pixel values in column-first order, again to be loaded by
				  `Shady.Linearization.LoadLUT()`.
				
				Finally you have the option of setting `None`, to disable the usage
				of look-up tables.
		
		Returns:
			A `LookupTable` instance.
		"""
		if not isinstance( value, LookupTable ):
			if isinstance( value, LinkGL ):
				self.Set( lookupTableTextureSize=value, lookupTableTextureSlotNumber=value, lookupTableTextureID=value )
				return self.lut
			elif value is not None:
				value = LookupTable( self.world(), value )
				
		if value is None: self.Set( lookupTableTextureSize=-1, lookupTableTextureSlotNumber=-1, lookupTableTextureID=-1 )
		else:             self.Set( lookupTableTextureSize=value.lookupTableTextureSize, lookupTableTextureSlotNumber=value.lookupTableTextureSlotNumber, lookupTableTextureID=value.lookupTableTextureID )
		if value is not self: self.__lut = value
		return value
		

	@classmethod
	def AddCustomUniform( cls, name=None, defaultValue=None, **kwargs ):
		"""
		Modifies the class (`World` or `Stimulus`) so that it possesses
		one or more new managed properties, whose values are then
		accessible from inside the fragment shader. This must be
		performed before `World` construction.
		
		Example::
		
			Shady.World.AddCustomUniform( 'spam', [1,2,3] )
			Shady.Stimulus.AddCustomUniform( eggs=4, beans=[5,6] )
		
		Either syntax can be used in either class. The keyword-argument
		syntax has the advantage of being able to define multiple new
		properties in one call.
		
		The default values you supply dictate whether the new property
		is 1-, 2-, 3- or 4-dimensional.  For a 1-dimensional property,
		the type of your default value also determines whether the
		property gets defined as an integer or floating-point variable.
		(2-, 3- or 4- dimensional properties are always re-cast as
		floating-point).
		
		The corresponding uniform variables are then automatically made
		available in the fragment shader code, with the first letter
		of the property name getting capitalized and a 'u' prepended.
		So, as a consequence of the two lines in the example above, the
		modified shader would then contain these definitions::
		
			uniform vec3 uSpam;
			uniform int uEggs;
			uniform vec2 uBeans;
		
		...all of which is useless unless you actually write some
		custom shader functions that access the new variables.
		
		See also:
			`AddCustomSignalFunction`,
			`AddCustomModulationFunction`,
			`AddCustomWindowingFunction`
		"""
		props = []
		for name, defaultValue in [ ( name, defaultValue ) ] + list( kwargs.items() ):
			if defaultValue is None or not name: continue
			prop = ManagedProperty( names=name.split(), default=defaultValue )
			floatingPoint = True in [ isinstance( x, float ) for x in prop.default ]
			numberOfElements = len( prop.default )
			if numberOfElements == 1:
				if floatingPoint: uType = 'float'; prop.transfer =  'glUniform1f'
				else:             uType = 'int'  ; prop.transfer =  'glUniform1i'
			else:
				uType = 'vec%d' % numberOfElements
				prop.transfer =  'glUniform%df' % numberOfElements # TODO: in later GLSL versions we could have integer vectors
				if numberOfElements not in [ 2, 3, 4 ]: raise ValueError( 'new property must have 1, 2, 3 or 4 elements' )
			cls._AddCustomProperty( prop, index=-1 )
			fieldname = '_custom_properties'
			registry = getattr( cls, fieldname, [] )
			setattr( cls, fieldname, registry )
			registry.append( prop )
			uName = 'u' + prop.name[ 0 ].upper() + prop.name[ 1: ]
			declarations = World._substitutions[ 'CUSTOM_UNIFORMS' ]
			declaration = 'uniform %s %s;' % ( uType, uName )
			if declarations.get( prop.name, '' ) != declaration:
				declarations[ prop.name ] = declaration
			props.append( prop )
		return props

def AddCustomSignalFunction( code ):
	"""
	Defines a new signal function in the fragment shader.
	
	Must be called, *before* construction of your `World`.  The `code`
	argument is a (usually triple-quoted multi-line) string containing
	the complete definition of a function in GLSL.
	
	The protoype for the function may be one of the following::
	
		float MySignalFunction( vec2 xy ) { ... }
		vec3  MySignalFunction( vec2 xy ) { ... }
	
	where `xy` are coordinates measured in pixels relative to the
	center of the stimulus. Obviously we're using `MySignalFunction`
	here as a placeholder---use your own descriptive name for the
	new function. Your function must `return` either a floating-point
	signal value, or three-dimensional (red, green, blue) signal
	value.  If non-negative values have been supplied in a
	`Stimulus` instance's `.color` property, your signal function
	will get multiplied by these. Then, any desired contrast modulation
	and windowing will be applied. Then, the result will be added to
	the `.backgroundColor`.
	
	Your new function can be applied to a `Stimulus` instance `stim`
	as follows::
	
		stim.signalFunction = Shady.SIGFUNC.MySignalFunction
	
	If you want to parameterize your new function further, you can
	use the existing `uniform vec4 uSignalParameters` variable, which
	is linked to the `Stimulus.signalParameters` property. You can also
	define your own additional properties/uniform variables with
	the `AddCustomUniform()` class method.
	
	See also:
		`AddCustomModulationFunction`,
		`AddCustomWindowingFunction`
		`World.AddCustomUniform`,
		`Stimulus.AddCustomUniform`,
	"""
	return _AddCustomFunction( code, enum=SIGFUNC,
		switchSection='SIGNAL_FUNCTION_CALLS', switchName='uSignalFunction',
		returnTypes=[ 'float', 'vec3' ],
		functionCall='signal = Tint( {functionName}( xy ), uColor );',
	)
	
def AddCustomModulationFunction( code ):
	"""
	Defines a new contrast-modulation function in the fragment
	shader.
	
	Must be called *before* construction of your `World`.  The `code`
	argument is a (usually triple-quoted multi-line) string containing
	the complete definition of a function in GLSL.
	
	The protoype for the function must be::
	
		float MyModulationFunction( vec2 xy ) { ... }
	
	where `xy` are coordinates measured in pixels relative to the
	center of the stimulus. Obviously we're using `MyModulationFunction`
	here as a placeholder---use your own descriptive name for the
	new function. Your function must `return` a floating-point
	contrast multiplier.
	
	Your new function can be applied to a `Stimulus` instance `stim`
	as follows::
	
		stim.modulationFunction = Shady.MODFUNC.MyModulationFunction
	
	If you want to parameterize your new function further, you can
	use the existing `uniform vec4 uModulationParameters` variable,
	which is linked to the `Stimulus.modulationParameters` property.
	You can also define your own additional properties/uniform variables
	with the `AddCustomUniform()` class method.
	
	See also:
		`AddCustomSignalFunction`,
		`AddCustomWindowingFunction`
		`World.AddCustomUniform`,
		`Stimulus.AddCustomUniform`,
	"""
	return _AddCustomFunction( code, enum=MODFUNC,
		switchSection='MODULATION_FUNCTION_CALLS', switchName='uModulationFunction',
	)
	
def AddCustomWindowingFunction( code ):
	"""
	Defines a new spatial windowing function in the fragment shader.
	
	Must be called *before* construction of your `World`.  The `code`
	argument is a (usually triple-quoted multi-line) string containing
	the complete definition of a function in GLSL.
	
	The protoype for the function must be::
	
		float MyWindowingFunction( float r ) { ... }
	
	where the domain of `r` if from 0 (in the center of the `Stimulus`,
	or indeed anywhere on its plateau if it has one) to 1 (at outer
	edge of the largest oval that fits in the `Stimulus` bounding box).
	Obviously we're using `MyWindowingFunction` here as a placeholder---
	use your own descriptive name for the new function. Your function
	must `return` a floating-point contrast multiplier.
	
	Your new function can be applied to a `Stimulus` instance `stim`
	as follows (bearing in mind that a negative `.plateauProportion`
	value disables windowing entirely)::
	
		stim.windowingFunction = Shady.WINFUNC.MyWindowingFunction
		stim.plateauProportion = 0
	
	If you want to parameterize your new function further, you can
	define your own additional properties/uniform variables with the
	`AddCustomUniform()` class method.
	
	See also:
		`AddCustomSignalFunction`,
		`AddCustomModulationFunction`
		`World.AddCustomUniform`,
		`Stimulus.AddCustomUniform`,
	"""
	return _AddCustomFunction( code, enum=WINFUNC,
		switchSection='WINDOWING_FUNCTION_CALLS', switchName='uWindowingFunction',
		requiredInputType='float', returnTypes=[ 'float' ],
		functionCall='lambda *= {functionName}( rlen );',
	)

class PRESCREENING( object ):
	Nothing = 0
def AddCustomPrescreeningFunction( code ):
	if 'prescreeningFunction' not in World._substitutions[ 'CUSTOM_UNIFORMS' ]:
		World.AddCustomUniform( prescreeningFunction=0 )
	return _AddCustomFunction( code, enum=PRESCREENING,
		switchSection='PRESCREENING_FUNCTION_CALLS', switchName='uPrescreeningFunction',
		requiredInputType='void', returnTypes='void',
		functionCall='{functionName}();',
	)
	
class POSTPROCESSING( object ):
	Nothing = 0
def AddCustomPostprocessingFunction( code ):
	if 'postprocessingFunction' not in World._substitutions[ 'CUSTOM_UNIFORMS' ]:
		World.AddCustomUniform( postprocessingFunction=0 )
	return _AddCustomFunction( code, enum=POSTPROCESSING,
		switchSection='POSTPROCESSING_FUNCTION_CALLS', switchName='uPostprocessingFunction',
		requiredInputType='vec4', returnTypes='vec4',
		functionCall='gl_FragColor = {functionName}( gl_FragColor );',
	)

def AlternativesString( sequence, transformation=repr, conjunction='or' ):
	sequence = [ transformation( x ) for x in sequence ]
	return ', '.join( sequence[ :-1 ] ) + ( ( ' %s ' % conjunction ) if len( sequence ) > 1 else '' ) + sequence[ -1 ]

def _AddCustomFunction( code, switchSection, switchName, returnTypes=( 'float', ), functionCall='f = {functionName}( xy );', requiredInputType='vec2', enum=None ):
	tokens = re.findall( r'\w+|[^\w\s]+', code )
	returnType, functionName, openParenthesis, inputType, inputName, closeParenthesis = ( tokens + [ '' ] * 6 )[ :6 ]
	if inputType == 'void' and inputName == ')': inputName, closeParenthesis = '', ')'
	if openParenthesis != '(': raise ValueError( 'must start with a valid function prototype' )
	if not isinstance( returnTypes, ( tuple, list ) ): returnTypes = [ returnTypes ]
	if returnType not in returnTypes: raise ValueError( 'function must return type %s' % AlternativesString( returnTypes, lambda x: '`%s`' % x ) )
	if inputType != requiredInputType or closeParenthesis != ')': raise ValueError( 'must be a function of a single `%s` typed input' % requiredInputType )
	bodyRegistry = World._substitutions[ 'CUSTOM_FUNCTIONS' ]
	#if code != bodyRegistry.get( functionName, code ): raise ValueError( 'code does not match previously-registered definition of custom function %s' % functionName )
	bodyRegistry[ functionName ] = code
	switchRegistry = World._substitutions[ switchSection ]
	offset = 2 # 0 is no function, 1 is SinewaveSignal or SinewaveModulation
	if functionName in switchRegistry: return offset + list( switchRegistry.keys() ).index( functionName )
	switchNumber = offset + len( switchRegistry )
	switchCode = '\telse if( {switchName} == {switchNumber} ) {{' + functionCall + '}}'
	switchCode = switchCode.format( switchName=switchName, switchNumber=switchNumber, functionName=functionName )
	switchRegistry[ functionName ] = switchCode
	if enum: setattr( enum, functionName, switchNumber )
	return switchNumber	

ALL_WORLDS = []
def CloseAllWorlds():
	while ALL_WORLDS:
		try: ref = ALL_WORLDS.pop( 0 )
		except: break
		world = ref()
		if not world: continue
		try: world.Close()
		except: pass
def WaitForAllWorlds():
	while True:
		for ref in ALL_WORLDS:
			world = ref()
			if world and world.state in [ 'running' ]: break
		else: return
		time.sleep( 0.010 )
		
@ClassWithManagedProperties._Organize
class World( LinkGL ):
	"""
	A `World` instance encapsulates the window and rendering environment in which you
	draw stimuli. By default, a `World` will fill one screen, but its size, offset and
	decoration can also be tailored explicitly if necessary. When you initialize a
	`World`, Shady creates an OpenGL program and compiles and links a vertex shader
	and a fragment shader to it: this is what allows signal generation, contrast
	modulation, windowing, gamma correction and dithering to be performed on the
	graphics processor.
	
	Once you have created the `World`, you will probably want to call need to 
	call the `.Stimulus()` method one or more times, to configure the things that
	should be drawn in it.
	
	Args:
		width (int):
			width of drawable area in "screen coordinates" (which usually means pixels,
			but see the note below).
		height (int):
			height of drawable area in "screen coordinates" (which usually means pixels,
			but see the note below).
		size (int, tuple or list):
			width and height of drawable area in "screen coordinates" (see note below).
			If this is a single number, it is used for both width and height. If it is
			a `tuple` or `list`, it is interpreted as [width, height]. However, the
			separate `width` and/or `height` arguments take precedence, if supplied.
		left (int):
			horizontal offset from the edge of the screen, in "screen coordinates"
			(which usually means pixels, but see the note below).
		top (int):
			vertical offset from the top of the screen, in "screen coordinates"
			(which usually means pixels, but see the note below).
		
		screen (int):
			Screen number.  0 or `None` (default) means use whichever is designated
			as the primary screen.  A positive integer explicitly selects a screen
			number.  The output of the global `Screens()` function may help you choose
			the screen number you want.
		
		threaded (bool):
			If you specify `threaded=False`, the `World`'s main rendering/event-
			processing loop will not be started automatically:  you will have to start
			it yourself, from the appropriate thread, using the `.Run()` method. 
			In this case, the best way to perform initial `World` configuration and
			`Stimulus` creation is to put the code in the body of a `Prepare()` method
			that you specify by subclassing `World`.
			
			With `threaded=True`, a new thread will be created to perform all the
			work of `World` construction and then, automatically, to run the main loop.
			Any subsequent call to the `.Run()` method will do nothing except
			sleep until the thread ends.  This is the easiest way to use Shady: you
			can then create and manipulate stimuli either from a `Prepare` method, or
			from wherever else you want. This appears to work well on Windows, but
			will have problems (which can only partially be worked-around) on other
			operating systems: see the `Shady.Documentation.Concurrency` docstring
			:doc:`or click here <../auto/Concurrency>`.
		
		canvas (bool):
			If you set this to `True` a "canvas" `Stimulus` instance will be
			created automatically, filling the screen behind other stimuli.  If you
			do not create one automatically like this, you can do it later by calling
			the `.MakeCanvas()` method.   A canvas allows gamma-correction and
			dynamic-range enhancement tricks to be performed on the backdrop as well
			as on your foreground stimuli, and it allows the `World`'s "atmosphere"
			properties (`.backgroundColor`,  `.gamma`, `.noiseAmplitude` and friends)
			to take effect: see the `Shady.Documentation.PreciseControlOfLuminance`
			docstring :doc:`or click here <../auto/PreciseControlOfLuminance>`.
		
		frame (bool):
			Whether or not to draw a frame and title-/drag- bar around the window.
		
		fullScreenMode (bool):
			Default behavior is to create a window that exactly covers one screen.
			This can be done by creating an ordinary window that just happens to be
			the same size as the screen (`fullScreenMode=False`) or by actually asking
			the system to change to full-screen mode (`fullScreenMode=True`).  The
			default on Windows is `False`, since it allows you to switch windows (e.g.
			with alt-Tab) and still have the Shady window visible in the background
			(note however, that background windows have poor timing precision - to
			render precisely without skipping frames you will need to keep the window
			in the foreground).  With `fullScreenMode=True` this is impossible: the
			window will disappear when it loses focus.  On the Mac, the default
			setting for full-sized windows is `fullScreenMode=True`, because this
			seems to be the only way to hide the menu bar at the top of the screen.
			
			For non-full-sized windows, the default is `fullScreenMode=False`. If
			you set it to `True` while also explicitly designating the size of the
			`World`, the OS will attempt to change resolution.  This will probably be
			a bad idea for psychophysical applications on most modern screens: for
			rendering accuracy, you should address the screen at its native
			(maximum) resolution.
		
		visible (bool):
			If you set this to `False`, the window will be created off-screen and
			will only become visible when you set its `.visible` property to `True`.
		
		debugTiming (bool):
			Every `World` records the timing intervals between its frame callbacks,
			to aid in analyzing timing performance. If you set `debugTiming=True`,
			it will record additional information that breaks down the allocation
			of this time.  By default the setting will be propagated to every
			`Stimulus` instance as well (set each `stim.debugTiming=False` if this
			is not what you want---if there are many stimuli, then the timing debug
			calls themselves can start to have a measurable impact on performance).
		
		logfile (str):
			Optionally specify the name of a text file which will log various
			pieces of useful diagnostic information. If your filename includes
			the substring `{}`, this will be replaced by a `yyyymmdd-HHMMSS`
			local timestamp. If the file stem ends with `-full` then 
			`self.logger.logSystemInfoOnClose` will be set to `True` by default
			which means that a third-party program will be run when the `World`
			closes, to record extensive system information (NB: on Windows the
			program is `dxdiag.exe` which is time-consuming and produces lengthy
			logs).  You can write to the log file yourself with `self.logger.Log()`
			
		reportVersions (bool):
			If this is `True`, the `World` instance will call its `.ReportVersions()`
			method to report version information to the console, as soon as it is
			set up.
		
		**kwargs:
			Managed property values can also be specified as optional keyword
			arguments during construction, for example::
	
				w = World( ..., clearColor=[0,0,0.5], ... )
	
	Note:  The easiest way to create a `World` is by omitting all geometry arguments.
	Then it will fill the display screen (the primary screen by default, but you can
	also specify the `screen` number explicitly).   However, *if* you choose to use
	explicit geometry arguments (`width`, `height`, `size`, `left`, `top`) note that
	they are all in "screen coordinates".  Screen coordinates usually correspond to
	pixels, but in some systems (Macs with Retina screens) you may need to specify
	some fixed smaller proportion of the number of addressable pixels you actually
	want: for example, on a Late-2013 Macbook with 13-inch Retina screen,
	`w = World(1280, 800)` opens a window that actually has double that number of
	addressable pixels (2560 x 1600).    After construction, `w.size` will indicate
	the correct (larger) number of pixels.   Unfortunately, *before* construction,
	I have not yet found a general way of predicting the relationship between
	screen coordinates and pixels.
	"""
	_doc_cut = """
		syncType:
		
			* -1 (default) to try everything and see what works first
			*  0 disables `WaitForNextFrame()` entirely
			*  1 for `GL_NV_fence`  (NVidia only)
			*  2 for `glFenceSync` (supposedly OpenGL 3.2+ only *but* it does work
			     in some macOS legacy contexts)
			*  3 for `glBegin()`: worked in macOS legacy contexts; will fail
			     (hopefully silently) in modern contexts 
			
		openglContextVersion:
			Insist puritanically on a particular OpenGL context version. For
			example, supply 330 to get an OpenGL 3.3 context.  330+ means "modern"
			OpenGL and is supported by the windowing backend in the accelerator,
			but not by pyglet. `openglContextVersion=0` to fall back to
			a "legacy" or legacy-compatible context. On the Mac, 0 gives you a
			pure legacy context (OpenGL 2.1 + GLSL 1.2) that prevents you using
			anything from later versions (unfortunately including the nicer GLSL
			random-number generator), whereas 330 gives you a pure "modern" context
			that prevents you from using legacy features (like the ability to
			vary the width of drawn lines) and legacy drawing commands. On Windows,
			`openglContextVersion=0` is the default because it often leads to
			permissive settings in which legacy and modern stuff can be mixed, and
			this may be the most desirable option, regardless of whether you want
			to use legacy or  modern drawing commands (see the `legacy` argument
			below).
		legacy:
			`True` or `False` to specify whether legacy OpenGL (immediate-mode)
			draw commands should be used or not.  On Windows, the default is
			`None` which means the choice of legacy mode is guided by the value
			of `openglContextVersion`.  On the Mac, the default is `legacy=False`,
			which in turn causes `openglContextVersion` to default to 330
			instead of 0, because the Mac does not allow you to mix legacy and
			modern code in either direction. On Windows, `legacy` and
			`openglContextVersion` are semi-independent, in that
			`openglContextVersion=0` will typically allow you to choose to use
			either legacy *or* modern draw commands, or even a mixture of both;
			but if you explicitly specify `openglContextVersion`, legacy draw
			commands will fail---so in that case, `legacy=False` becomes the
			default (and only sensible) option.
		backend:
			an optional specification of the windowing back-end: see the global
			function `BackEnd()` which will be called automatically (with lasting
			effect) if you specify this argument and omit `window`. Generally, it
			is better to leave this as `None` and let the defaults take over.
		acceleration:
			an optional specification of the acceleration preference: see the global
			function `BackEnd()` which will be called automatically (with lasting
			effect) if you specify this argument.  Generally, it is better to leave
			this as `None` and let the defaults take over.
		profile:
			Can be `True` or `False`, or optionally can be a string specifying the
			exact profiler: `'cProfile'`, `'pyinstrument'` or  `'hotshot'` (those last
			two require the correspondingly-named third-party packages to be installed).
			Call `self.profile.enable()` to enable profiling of the Python code
			that is called on each frame. Examine `self.profile.stats()` after running
			the world.
		window:
			an optional instance of `Window` from one of the back-end `*Windowing`
			submodules. Generally it is better to leave this as `None` and let the
			`World` create its window automatically from whichever `BackEnd()`
			settings are currently configured.
	"""
	
	_substitutions = collections.defaultdict( collections.OrderedDict )
	_thread_hijacker = None
	
	def __init__( self,
		width=None, height=None, left=None, top=None, screen=None,
		threaded=True, canvas=False, frame=False, fullScreenMode=None, visible=True,
		openglContextVersion=None, legacy=None,
		backend=None, acceleration=None,
		debugTiming=False, profile=False, syncType=-1,
		logfile=None, reportVersions=False,
		window=None, **kwargs
	):
		
		ALL_WORLDS.append( weakref.ref( self ) )
		
		self.__state = 'starting'
		self.__pending = []
		self.__onClose = { 'before' : [], 'after' : [] }
		self.__fakeFrameRate = 0.0
		self.__event_handlers = {}
		self.__dacMax = None
		self.__dacBits = None
		self.__lastAnchor = None
		self.__lastDims = None
		self.SetEventHandler( self.HandleEvent )
		
		self.t0 = None
		
		self.logger = Logging.Logger( logfile )
		
		if backend is not None or acceleration is not None: BackEnd( backend, acceleration )
		kwargs.update( dict(
			width=width, height=height, window=window, left=left, top=top, screen=screen,
			canvas=canvas, frame=frame, fullScreenMode=fullScreenMode, visible=visible,
			openglContextVersion=openglContextVersion, legacy=legacy,
			debugTiming=debugTiming, profile=profile, syncType=syncType,
			reportVersions=reportVersions,
		) )
				
		if self.logger:
			sys.stderr.write( 'Logging to %s\n' % self.logger.filename )
			#self.logger.Divert( 'stdout' )
			self.logger.Divert( 'stderr' )
			self.logger.Log( world_construction=kwargs )
			self.AfterClose( lambda: self.logger.LogTimings( self ) )
			self.AfterClose( self.logger.Close )
	
		hijacker = self._thread_hijacker
		if hijacker: threaded = False
		if threaded and not sys.platform.lower().startswith( ( 'win', ) ):
			threaded = False
			sys.stderr.write( 'Cannot run in a background thread on %s. Running in main thread - so remember to call .Run()\n' % sys.platform )
		self.threaded = threaded
		self.thread = None
		if threaded:
			self._fatal = None
			def ConstructorThread():
				try: self._Construct( **kwargs )
				except: self._fatal = sys.exc_info(); return
				try: self.Run()
				except: self._fatal = sys.exc_info(); return
			self.thread = threading.Thread( target=ConstructorThread )
			self.thread.start()
			while self.__state != 'running' and self.thread.is_alive(): time.sleep( 0.1 )
			if self._fatal: reraise( *self._fatal )
		elif hijacker:
			hijacker.WaitFor( self._Construct, **kwargs )
			hijacker.Queue( self.Run )
			while self.__state != 'running' and hijacker.running: time.sleep( 0.1 )
			
		else:
			self._Construct( **kwargs )
			
	def _Construct( self, width, height, window, left, top, screen, canvas, frame, fullScreenMode, visible, openglContextVersion, legacy, debugTiming, profile, syncType, reportVersions, **kwargs ):
		# NB: if `window` is supplied, `width`, `height` and `size` arguments will be ignored
		size = kwargs.pop( 'size', None )
		if not window:
			if size is not None:
				if width is None or width <= 0:
					try: width, _ = size
					except: width = size
				if height is None or height <= 0:
					try: _, height = size
					except: height = size
			if height is None or height <= 0:
				try: width, height = width
				except: height = width
			window = LoadBackEnd().Window
			
		#on_macos   = sys.platform.lower().startswith( 'darwin' )
		on_windows = sys.platform.lower().startswith( 'win' )
		if legacy is None and openglContextVersion is None: legacy = on_windows # used to be True here
		if legacy is None and openglContextVersion is not None: legacy = openglContextVersion < 330
		if openglContextVersion is None and legacy is not None:
			if legacy or on_windows: openglContextVersion = 0   # on Windows, don't constrain openglContextVersion by default even if legacy==False, because the context will likely be permissive and *include* both legacy and modern support - only constrain context version if explicitly instructed to do so
			else: openglContextVersion = 330
		
		glslDirectory = PackagePath( 'glsl' )
		substitutions = '\n'.join( '//#%s\n%s' % ( key, '\n'.join( entries.values() ) ) for key, entries in self._substitutions.items() if entries )
		
		if callable( window ):
			window_kwargs = dict( screen=screen, frame=frame, fullScreenMode=fullScreenMode, visible=visible, openglContextVersion=openglContextVersion, legacy=legacy )
			if width  not in [ -1, None ]: window_kwargs[ 'width'  ] = width
			if height not in [ -1, None ]: window_kwargs[ 'height' ] = height
			if left   not in [ -1, None ]: window_kwargs[ 'left'   ] = left
			if top    not in [ -1, None ]: window_kwargs[ 'top'    ] = top
			if getattr( window, 'accelerated', False ):
				window_kwargs[ 'glslDirectory' ] = glslDirectory
				window_kwargs[ 'substitutions' ] = substitutions
				
			if hasattr( window, 'TabulaRasa' ): window.TabulaRasa()
			window = window( **window_kwargs )
		self.window = window
		self.window.excepthook = ExceptionHook
		self.window.on_close = self._RunOnClose
		self.width, self.height = self.window.size
		
		# TODO: must detect whether modern OpenGL was requested but failed to be delivered,
		#       and set legacy=True here if so
		self._legacy = legacy
		
		self._parentThread = threading.current_thread()
		self.profile = ProfileContextManager( mode=profile, report_streams=[ self.logger.Log ] if self.logger else None )
		
		if ShaDyLib:
			if getattr( self.window, 'accelerated', False ):
				# accelerated windowing and accelerated rendering: Never even calls self._Draw - the
				# only Python code that will be called on each frame is self._FrameCallback, after all
				# Shady-mode drawing is done. In this case the Window will have already created a Renderer
				# instance and called InitShading
				self._accel = self._Accelerate( self.window.GetRenderer(), size=self.size )
			else:
				# non-accelerated windowing, accelerated rendering: the Window is implemented by a Python wrapper
				# (pyglet, pygame)... and it calls the Python method self._Draw on each frame, which, instead of
				# doing most of its normal thing in Python, will detect the presence of self._accel and call the DLL
				# function self._accel.Draw(). That will in turn draw the Stimulus objects without
				# leaving the binary.
				self._program = ShaDyLib.InitShading( self.width, self.height, glslDirectory, substitutions )
				self._accel = self._Accelerate( ShaDyLib.Renderer( shaderProgram=self._program, legacy=self._legacy ), size=self.size )
				#if getattr( self.window, 'needs_help_with_vbl', False ): self._accel.SetSwapInterval( 1 ) # or -1....
			self._accel.WaitForFrames( syncType )
			self.ditheringDenominator = dacMax = float( self._accel.QueryDACMax() )
			for prop in [ World.ditheringDenominator, Stimulus.ditheringDenominator ]:
				if not prop.default_changed: prop.SetDefault( dacMax )
		else:
			# non-accelerated mode: no ShaDyLib, so everything is done from Python via the PyEngine sub-module.
			self._program = PyEngine.InitShading( glslDirectory, substitutions )
			self._accel = None
			#if getattr( self.window, 'needs_help_with_vbl', False ): PyEngine.GL.UseVBL() - fails
			if syncType != -1: print( 'syncType=%r ignored' % syncType ) 
			self.ditheringDenominator = dacMax = PyEngine.QueryDACMax( self._legacy )
			for prop in [ World.ditheringDenominator, Stimulus.ditheringDenominator ]:
				if not prop.default_changed: prop.SetDefault( dacMax )
		
		self.__dacMax = dacMax
		self.__dacBits = int( round( math.log( dacMax + 1 ) / math.log( 2 ) ) )
		self.stimuli = Bunch()
		self._Initialize( world=self, debugTiming=debugTiming ) # includes initialization of transfer list, for non-accelerated objects		
		prep = { k : kwargs.pop( k ) for k in list( kwargs.keys() ) if not hasattr( self, k ) }
			
		self.backend = self.window.__module__.split( '.' )[ -1 ].lower()
		if self.backend.endswith( 'windowing' ): self.backend = self.backend[ :-len( 'windowing' ) ]
		self.versions = ReportVersions( world=self, outputType='dict' )
		if self.logger: self.logger.Log( '\nversions = {\n%s\n}\n' % self.ReportVersions( outputType='string' ) )
		if reportVersions: self.ReportVersions()
		
		self.Set( **kwargs )
		if canvas: self.MakeCanvas()
		self.Prepare( **prep )
		
		if self.logger: self.logger.Log( world_size=tuple( self.size ), world_dacMax=self.dacMax )
		
	def Prepare( self, **kwargs ):
		"""
		This method is called after the `World` is initialized and the shader programs
		are set up, but before the first frame is actually rendered. It is carried out
		in the same thread as initialization and rendering.
		
		In the `World` base class, this method does nothing. However, if you create a
		subclass of `World`, you can overshadow this method. It is then a good place
		to perform initial `Stimulus` creation and other configuration specific to
		your particular application.  You can use any prototype you like for the method,
		as long as it has a `self` argument.
		
		When you first construct the `World`, any keyword arguments that are not
		recognized by the constructor will be automatically passed through to `Prepare()`.  
		"""
		if kwargs: print('.Prepare() arguments:\n%s\n' % '\n'.join( '  %s = %r' % item for item in sorted( kwargs.items() ) ) )
		
	def OnClose( self, func, *pargs, **kwargs ):
		when = 'before'
		if isinstance( func, str ) and pargs:
			when, func, pargs = func, pargs[ 0 ], pargs[ 1: ]
		if not func: return
		container = []
		queue = self.__onClose[ when ]
		queue.append( ( func, pargs, kwargs, container ) )
		return container
	
	def BeforeClose( self, func, *pargs, **kwargs ):
		"""
		This method registers a callable `func` (and optionally the `*pargs` and
		`**kwargs` that should be passed to it) that will be called just before
		the `World` closes. One way to use this method is as a decorator---for
		example::
		
			w = Shady.World()
			@w.BeforeClose
			def Goodbye():
				print( "goodbye" )
		
		Returns:
			an empty `list`. This has two uses: (1) when `func` is called, its
			return value will be inserted into this list; (2) the `id` of the
			list instance uniquely identifies the callback you have just
			registered, so it can be used as a handle for cancelling the
			function with `.CancelOnClose()`
		"""
		return self.OnClose( 'before', func, *pargs, **kwargs )
		
	def AfterClose(  self, func, *pargs, **kwargs ):
		"""
		This method registers a callable `func` (and optionally the `*pargs` and
		`**kwargs` that should be passed to it) that will be called just *after*
		the `World` closes. The method is otherwise identical to `.BeforeClose()`
		"""
		return self.OnClose( 'after',  func, *pargs, **kwargs )
	
	def CancelOnClose( self, container ):
		"""
		Cancels a callback that had previously been scheduled to run at closing
		time by either `.BeforeClose()` or `.AfterClose()`, either of which will
		have returned the `container` that you need to pass as the input argument
		here.
		"""
		for queue in self.__onClose.values():
			queue[ : ] = [ item for item in queue if item[ -1 ] is not container ]
	
	def _RunOnClose( self, whichQueue='before' ):
		queue = self.__onClose[ whichQueue ]
		while queue:
			func, pargs, kwargs, container = queue.pop( 0 )
			try: container.append( func( *pargs, **kwargs ) )
			except: self._excepthook( *sys.exc_info() )
	
	def CreatePropertyArray( self, propertyName, *stimuli ):
		"""
		This method returns a `PropertyArray` object which contains a `numpy`
		array. Each row of the array is the storage area for the named property
		of one of the specified stimuli.  You can still address the property
		of each individual `Stimulus` in the usual way, but now you also have
		the option of addressing them all at once in a single array operation,
		which may be much more efficient if there are many stimuli.
		
		Args:
			propertyName (str):
				The name (or alias) of a fully-fledge `ManagedProperty` of the
				`Stimulus` class (for example, `'color'` or `'position'`).
			
			*stimuli:
				This is flexible. You can pass the (string) names of `Stimulus`
				instances, or you can pass the instances themselves. You can pass
				them as separate arguments, and/or in tuples or lists. If you're
				using names, you can even pass them as a single space-delimited
				string if you want. 
		
		Returns:
			a `PropertyArray` instance whose `.A` attribute contains the `numpy`
			array.
		
		Example::
		
			import numpy, Shady
			w = Shady.World()
			p = numpy.linspace( -1.0, +1.0, 20, endpoint=True )
			stims = [ w.Stimulus( xy=w.Place( p_i, 0 ), bgalpha=0, pp=1 ) for p_i in p ]
			position = w.CreatePropertyArray( 'xy', stims )
			color = w.CreatePropertyArray( 'color', stims )
			@w.AnimationCallback
			def Animate( self, t ):
				s = Shady.Sinusoid( t, p * 180 )
				position.A[ :, 1 ] = 200 * s
				color.A[ :, 0 ] = 0.5 + 0.5 * s
				color.A[ :, 1 ] = 0.5 + 0.5 * s[ ::-1 ]
				color.A[ :, 2 ] = s ** 2
			# one call with a few simple efficient numpy array operations
			# instead of 20 stimuli x 4 shortcuts = 80 dynamic function calls
		"""
		stimuli = [ stimulus for x in stimuli for stimulus in ( x if isinstance( x, ( tuple, list ) ) else x.split() if hasattr( x, 'split' ) else [ x ] ) ]
		stimuli = [ ( self.stimuli[ x ] if isinstance( x, basestring ) else x ) for x in stimuli ]
		stimulusNames = [ stimulus.name for stimulus in stimuli ]
		propertyName = stimuli[ 0 ].GetPropertyDescriptor( propertyName ).name # canonicalize
		if not numpy: raise ImportError( 'to create property arrays, you will need the third-party package "numpy"' )
		if self._accel:  propertyArray = self._accel.CreatePropertyArray( propertyName, ' '.join( stimulusNames ) )
		else: propertyArray = PyEngine.PropertyArray( propertyName, stimuli )
		propertyArray.stimulusNames = stimulusNames
		propertyArray.propertyName = propertyName
		for stimulus, row in zip( stimuli, propertyArray.A ):
			descriptor = stimulus.GetPropertyDescriptor( propertyName )
			descriptor.determine_array( stimulus, name=propertyName, array=row )
			# TODO: this needs to be undone whenever an instance of PropertyArray (the class from ShaDyLib.py and the one from PyEngine.py) is destroyed...
		return propertyArray
		
	def _ProcessEvent( self, event ):
		# this indirect path to self.HandleEvent serves two purposes:
		# (1) it allows the HandleEvent method to be changed on the fly, using SetEventHandler
		# (2) it allows x and y coordinates to be transformed according to the World origin, and other World-specific transformations
		if event.x is not None:
			if self.pixelGrouping[ 0 ] > 0: event.x /= self.pixelGrouping[ 0 ]
			event.x += PartialTranslation( -self.size[ 0 ], self.anchor[ 0 ] )
		if event.y is not None:
			if self.pixelGrouping[ 1 ] > 0: event.y /= self.pixelGrouping[ 1 ]
			event.y += PartialTranslation( -self.size[ 1 ], self.anchor[ 1 ] )
		for key, handler in sorted( self.__event_handlers.items() ):
			if handler( event ): break
		
	def HandleEvent( self, event ):
		"""
		This method is called every time an event happens.  Its argument
		`event` is a standardized instance of class `Event`, containing
		details of what happened. The default (superclass) implementation
		responds when `event.type` is `'key_release'` and the released key
		is either the Q key or the escape key - this causes the window to
		close (and hence the drawing thread will terminate, if this `World`
		is threaded).
		
		You can overshadow this method in your `World` subclass, or you
		can replace it on an instance-by-instance basis using the method
		`.SetEventHandler()` or the decorator `.EventHandler()`- for example::
		
			def handler( self, event ):
			    print( event )
			w.SetEventHandler( handler )
		
		Note that, for each event, it is possible to have more than one
		handler, occupying different "slots" in the cascade that is applied
		to each event.  By default, the `HandleEvent` method occupies slot 0.
		
		"""
		#print( event )
		if event.type == 'key_release' and event.key in [ 'escape', 'q' ]: self.window.Close()
		
	def SetEventHandler( self, handler, slot=0 ):
		"""
		Bind the callable `handler` as part of the instance's cascade of event
		handlers. The `slot` argument determines the serial order in which handlers
		are run on each event (negative numbers before positive). If `handler` is
		`None`, any handler currently occupying the specified slot is removed.
		
		By default, the class's `HandleEvent()` method is registered in slot 0.
				
		The prototype for an event handler can be `handler(self, event)`
		or just `handler(event)`.   If the handler returns anything that
		evaluates to `True` in the boolean sense, that's the signal to abort the
		cascade of handlers for the event in question (i.e. skip the handlers
		in higher-numbered slots, this time around).
		
		Example::
		
			def handler( self, event ): 
				print( event )
			w = Shady.World().SetEventHandler( handler, slot=-1 )
		
		There is also a decorator version of the same operation, simply called
		`.EventHandler()`::
		
			w = Shady.World()
			@w.EventHandler( slot=-1 )
			def handler( self, event ):
				print( event )
			
		"""
		self._BindCallable( 'HandleEvent', handler, numberOfArgsAfterSelf=1, container=self.__event_handlers, slot=slot )
		return self
		
	def EventHandler( self, slot=0 ):
		"""
		Decorator version of `.SetEventHandler()`
		
		Examples::
		
			w = Shady.World()
			
			@w.EventHandler    # overwrites default slot=0
			def handler( self, event ):
				print( 'handler got %s event' % event.type )
			
			@w.EventHandler( slot=1 )   # uses an explicit slot
			def handler2( self, event ):
				print( 'handler2 got %s event' % event.type )

		"""
		if callable( slot ): func = slot; return self.SetEventHandler( func ) and func
		return lambda func: self.SetEventHandler( func, slot=slot ) and func
	
	def BoundingBox( self, worldCoordinates=False ):
		"""
		This method returns the `World`'s bounding box, in pixels.
		
		Args:
			worldCoordinates (bool):
				If `True`, then the `left` and `bottom` coordinates are computed relative
				to the `World`'s own `.anchor` (so that gives you the bounding box within
				which you can draw stimuli, in coordinates a `Stimulus` would understand).
				If `False`, then `left = bottom = 0`.
		
		Returns:
			`[left, bottom], [width, height]` pixel coordinates for the `World`.
		"""
		w, h = self.size
		return [
			PartialTranslation( -w, self.anchor[ 0 ] ) if worldCoordinates else 0,
			PartialTranslation( -h, self.anchor[ 1 ] ) if worldCoordinates else 0,
		], [ w, h ]
		
	def _Draw( self, dt=None, t=None ):
		with self.profile.running:
			if self._accel: self._accel.Draw()
			else:           PyEngine.DrawWorld( self, dt=dt, t=t )
		
	def Run( self ):
		"""
		If the `World` was created with `threaded=True` and is already rendering,
		then this method does nothing except sleep in the current thread until the
		`World` has finished. If the `World` was not created threaded, then this
		method is required to actually execute its main rendering loop. Either way,
		the method does not return until the `World` closes.  
		"""
		if self.__state == 'running':
			while self.__state == 'running': time.sleep( 0.020 )
			return self
		self.__state = 'running'
		self.window.Run( render_func=self._Draw, event_func=self._ProcessEvent )
		self.__state = 'finished'
		return self
	
	@property
	def shady_stimuli( self ): return { k : v  for k, v in self.stimuli.items() if IsShadyObject( v ) }
	@property
	def foreign_stimuli( self ): return { k : v  for k, v in self.stimuli.items() if not IsShadyObject( v ) }
	@property
	def state( self ): return self.__state
	@property
	def dacMax( self ): return self.__dacMax
	@property
	def dacBits( self ): return self.__dacBits

	# Begin managed properties ############################################################
	
	size = ( width, height ) = ManagedProperty(
		default = [ -1, -1 ],
		transfer = 'self._ComputeWorldNormalizer',
		doc = """
			This is a pair of integers denoting the width and height of the `{cls}` in pixels.
			Do not attempt to change these values - it will not alter the size of the window
			and may have unexpected side effects.
		"""
	)
	clearColor = ( red, green, blue ) = ManagedProperty(
		default = [ 0, 0.5, 0 ],
		default_string = 'varies according to `BackEnd()` settings',
		transfer = 'glClearColor_RGB',
		doc = """
			This is a triplet of numbers in the range 0 to 1. It specifies the color of the empty screen.
			Note that these values are never linearized or dithered. For more precise control over the background,
			construct your `{cls}` with the argument `canvas=True` and then you can manipulate `.backgroundColor`,
			`.gamma`, '.ditheringDenominator' and `.noiseAmplitude`.
		""",
	)
	anchor__ = ( ax_n__, ay_n__ ) = ( anchor_x, anchor_y ) = origin = ( ox_n, oy_n ) = ( origin_x, origin_y ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'self._ComputeWorldProjection',
		doc = """
			This is a pair of numbers specifying where, in normalized coordinates within the rendering area of the window, pixel
			coordinate (0,0) should be considered to be for Stimulus positioning. An origin of [-1,-1]
			means the bottom left corner; [0,0] means the center; [+1,+1] means the top right corner.
			Translations resulting from a change in `.anchor` are automatically rounded down to an
			integer number of pixels, to avoid `.anchor` becoming an unexpected source of interpolation
			artifacts.
		""",
	)
	perspectiveCameraAngle = ManagedProperty( 0.0 )
	matrixWorldNormalizer = ManagedProperty( IDENTITY4FV, transfer = 'glUniformTransformation4' )
	matrixWorldProjection = ManagedProperty( IDENTITY4FV, transfer = 'glUniformTransformation4' )
	framesCompleted = ManagedProperty(0, transfer = 'glUniform1i' )
	timeInSeconds__ = t = ManagedProperty(
		default = 0.0,
		doc="This is a floating-point scalar value indicating the time in seconds since the `World` started rendering.",
	)
	visible__ = on = ManagedProperty(
		default = 1,
		doc = """
			This is a scalar boolean value indicating whether or not the `World` should be visible or not. On Windows
			the transition from visible to invisible and back is reasonably instantaneous. On the Mac you may have to
			endure the minimize/restore animation (although this is backend-dependent).
		""",
	)
	
	# properties that are not used directly, but are shared with the canvas Stimulus, if it exists:
	backgroundColor__ = bgcolor = bg = ( bgred, bggreen, bgblue ) = ManagedProperty(
		default = [ 0.5, 0.5, 0.5 ],
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the `.backgroundColor` of the background canvas Stimulus, if present (the `{cls}`
			needs to be constructed with the `canvas=True`, or you otherwise need to call `.MakeCanvas()` ).
			When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	noiseAmplitude__ = noise = ( rednoise, greennoise, bluenoise ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		doc = """
			This is a triplet of floating-point numbers corresponding to red, green and blue channels.
			It specifies the `.noiseAmplitude` for the background canvas
			Stimulus, if present (the `{cls}` needs to be constructed with the `canvas=True`, or you otherwise
			need to call `.MakeCanvas()` ). When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	lookupTableTextureSize = ManagedProperty( [ -1, -1, -1, -1 ] )  # also placeholder properties for sharing with canvas
	lookupTableTextureSlotNumber__ = slot = ManagedProperty( -1 )
	lookupTableTextureID = ManagedProperty( -1 )  # TODO: How can 'slot' be an alias for both props?
	gamma = ( redgamma, greengamma, bluegamma ) = ManagedProperty(
		default = [ 1.0, 1.0, 1.0 ],
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the `.gamma` of the background canvas Stimulus, if present (the `{cls}` needs to be
			constructed with the `canvas=True`, or you otherwise need to call `.MakeCanvas()` ).
			When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
			
			`.gamma = 1` is linear; `.gamma = -1` gives you the sRGB gamma profile (a piecewise function
			visually very similar to `.gamma = 2.2`)
			
			Note that `gamma` is ignored for stimuli that use a `.lut`
		""",
	)
	ditheringDenominator__ = dd = ManagedProperty(
		default = 0.0,
		default_string = 'dithering enabled (value determined automatically)',
		doc = """
			This is a floating-point number. It should be 0 or negative to disable dithering, or otherwise
			equal to the maximum DAC value (255 for most video cards). It specifies the `.ditheringDenominator`
			for the background canvas Stimulus, if present (the `{cls}` needs to be constructed with the
			`canvas=True`, or you otherwise need to call `.MakeCanvas()` ). When a canvas is created, this
			property of the `{cls}` is automatically linked to the corresponding property of the canvas
			`Stimulus` instance; if there is no canvas then this property is unused, although you may wish to
			link it explicitly to other stimuli with `.ShareProperties()` or `.LinkPropertiesWithMaster()`.
		""",
	)
	outOfRangeColor = ManagedProperty(
		default = [ 1.0, 0.0, 1.0 ],
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the `.outOfRangeColor` for the background canvas Stimulus, if present (the `{cls}`
			needs to be constructed with the `canvas=True`, or you otherwise need to call `.MakeCanvas()` ).
			When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	outOfRangeAlpha = ManagedProperty(
		default = 1.0,
		doc = """
			This is a number in the range 0 to 1. It specifies the `.outOfRangeAlpha` for the background
			canvas Stimulus, if present (the `{cls}` needs to be constructed with the `canvas=True`, or you
			otherwise need to call `.MakeCanvas()` ). When a canvas is created, this property of the `{cls}` is automatically linked to
			the corresponding property of the canvas `Stimulus` instance; if there is no canvas then this property is unused,
			although you may wish to link it explicitly to other stimuli with `.ShareProperties()` or
			`.LinkPropertiesWithMaster()`.
		""",
	)
	pixelReinterpretation = ManagedProperty( default = 0.0, transfer = 'glUniform1f' )
	pixelGrouping = ManagedProperty( default = [ 0.0, 0.0 ], transfer = 'glUniform2f' )
	""" Developer note on pixelGrouping:
	Explicit rounding, in the shader, to the nearest screen pixel location, is disabled
	by default. However you can see the tiny rounding errors this creates if you create,
	for example, a signal function that hits exactly 0 at multiple places on top of a
	background value of 0.5, such as::
	
	    Shady.AddCustomSignalFunction('''
	        float Tartan(vec2 p) { p = mod(p, 2.0); return 0.25 * (p.x - p.y); }
	    ''')
	    w=Shady.World(fullScreenMode=0,bitCombiningMode=1);s=w.Stimulus(sigfunc=Shady.SIGFUNC.Tartan)
	
	Compare this under `w.pixelGrouping = 0` with `w.pixelGrouping = 1` but be aware that
	(a) the differences are tiny, rounding to values 1/65535th apart and only visible
	because of the red-green split, (b) pixel rounding is not computationally trivial on
	the GPU - it requires a per-fragment matrix multiplication.
	
	You can change the default with `Shady.World.SetDefault( pixelGrouping=1 )` - then
	this setting will be respected automatically whenever you change to
	`w.bitCombiningMode=0` or `w.bitCombiningMode=1`.
	"""
	
	# End managed properties ############################################################
	
	@property
	def projectionMatrix( self ):
		return numpy.asmatrix( self.matrixWorldNormalizer ).reshape( [ 4, 4 ] ) * numpy.asmatrix( self.matrixWorldProjection ).reshape( [ 4, 4 ] )
	
	@call
	def fakeFrameRate():
		doc = """
		By default, with `.fakeFrameRate` equal to `None`, a `World` will try to update
		itself at the frame rate of the display hardware (though of couse it may end up
		being slower if you are doing too much computation between frames, or if there
		are other tasks that are using too many CPU or GPU resources).  The time argument
		`t` that gets passed into animation callbacks and dynamic property evaluations
		will reflect the real wall-time at which each frame is drawn.
		
		However, if you set `.fakeFrameRate` to a positive value, now frames can take
		as long as they like in real time, and the `t` argument will reflect the
		theoretical amount of time passed based on the number of frames completed,
		assuming the specified frame rate. This allows you to run animations in
		slower-than-real time.  One of the main applications would be for capturing
		stills or movies of `World` animation (the capture operation itself tends to be
		slow).
		
		If you do not fully understand the explanation above, do not change this
		property. It should be left as `None` whenever you want to display time-accurate
		animation (which should be the case under nearly all circumstances).
		"""
		def fget( self ): return self.__fakeFrameRate if ( self.__fakeFrameRate and self.__fakeFrameRate > 0.0 ) else None
		def fset( self, value ):
			if not value or value < 0.0: value = 0.0
			self.__fakeFrameRate = float( value )
		return property( fget=fget, fset=fset, doc=doc )
		
	def RunDeferred( self, func, *pargs, **kwargs ):
		"""
		`.Defer()` a function, then wait for it to run, and then return the output.
		NB: you'll wait forever if the `World` is not running...
		
		Note that you do not need to do this for most `World` methods: they have
		already been wrapped so that they run deferred when necessary and appropriate.
		"""
		return DeferredCall( func, context=self )( *pargs, **kwargs )

	def Defer( self, func, *pargs, **kwargs ):
		"""
		Any method that actually makes GL calls, such as `.NewPage()` or `.LoadTexture()`,
		must be called from the same thread/context as the one where all other
		GL operations happen, otherwise you may fail to see any result and/or the
		program may crash.  This is a workaround: if you call (for example)
		`self.Defer( func, arg1, arg2, ... )` then `func(arg1, arg2, ...)` will be
		called at the end of the next frame.
		
		This function is already used, under-the-hood, by the `@DeferredCall`
		method decorator, to make methods like `World.Stimulus` or `Stimulus.NewPage`
		safe. So there may be relatively few cases in which you need to use it directly.
		
		Args:
		    func:
		        this is the callable object to be called at the end of the next frame.
		        Optionally, you may influence the order in which these pending tasks
		        are performed by supplying a tuple `(priority, func)` instead of just
		        `func`.  The numeric value `priority` defaults to `0`. The higher its
		        value, the earlier the task will be performed, relative to other
		        pending tasks.
		    
		    *pargs and **kwargs:
		        any additional positional arguments, and any keyword arguments, are
		        simply passed through to `func` when it is called.
		
		Returns:
			An empty list. When `func` is finally called, its output will be inserted
			into this list. If `func` causes an exception to be raised, the stack
			trace information will be wrapped in a `DeferredException` instance and
			returned in the list.  The list also serves as a handle by which you can
			`Undefer()` a deferred task.
		"""
		pending = self.__pending
		if pending is None: pending = self.__pending = []
		container = []
		if isinstance( func, ( tuple, list ) ): priority, func = func
		else: priority = 0
		serialNumber = len( pending )
		pending.append( ( -priority, serialNumber, func, pargs, kwargs, container ) ) # NB: ensure container is last
		return container
		
	def Undefer( self, target_container ):
		"""
		Cancels a pending task that has been scheduled by `Defer() `to run at the
		end of the next frame.  Its input argument is the output argument of `Defer()`.
		"""
		self.__pending[ : ] = [ item for item in self.__pending if item[ -1 ] is not target_container ]
		
	def _RunPending( self ):
		pending = sorted( self.__pending, key=lambda x: x[ :2 ] )
		self.__pending[ : ] = []
		for priority, serialNumber, func, pargs, kwargs, container in pending:
			try: result = func( *pargs, **kwargs )
			except: result = DeferredException( *sys.exc_info() )
			container.append( result )
	
	def _SortStimuli( self ):
		if self._accel:
			stimuli = self.stimuli
			shady_names = self._accel.GetStimulusOrder().split()
			foreign_names = list( set( stimuli.keys() ) - set( shady_names ) )
			ss = self._shady_stimuli = [ stimulus for name in shady_names for stimulus in [ stimuli.get( name, None ) ] if stimulus is not None ]
			fs = self._foreign_stimuli = [ stimuli[ name ] for name in foreign_names ]
			fs[ : ] = [ stimulus for stimulus in fs if hasattr( stimulus, 'draw' ) or hasattr( stimulus, 'Draw' ) ]
			fs.sort( key=StimulusSortKey )
		else:
			ss = self._shady_stimuli = []
			fs = self._foreign_stimuli = []
			for name, stimulus in self.stimuli.items():
				if IsShadyObject( stimulus ): ss.append( stimulus )
				elif hasattr( stimulus, 'draw' ) or hasattr( stimulus, 'Draw' ): fs.append( stimulus )
			ss.sort( key=StimulusSortKey )
			fs.sort( key=StimulusSortKey )
	
	def _Clock( self ):
		# self.__fakeFrameRate is not used here because we're actually interested in wall time
		if self._accel: return self._accel.Seconds()
		else: return Timing.Seconds()
	
	def _FrameCallback( self, t, userPtr=None ):
		with self.profile.running:
			# To begin with, t is an absolute wall time in seconds, passed through from the windowing framework:
			# - it should have been measured *before* any GPU commands were issued for this frame, as close as possible to the SwapBuffers call (PygletWindowing with auto=True has a problem there);
			# - it is not guaranteed to be expressed relative to any particular epoch/origin
			#sys.stdout.write('*** entered _FrameCallback ***\n'); sys.stdout.flush()
			wallTimeAtCall = self._drawTime = t # record the absolute time at which the parent Draw() or DrawWorld() function was called - this is used by any subsequent _DebugTiming calls (PyEngine.DrawWorld also performs this assignment, so it's redundant in non-accelerated implementations but it doesn't hurt)
			if self.t0 is None:
				self.t0 = wallTimeAtCall
				self.window.SynchronizeEvents( wallTimeAtCall, self._Clock() )
			if self.__fakeFrameRate:
				worldTime = self.timeInSeconds = self.framesCompleted / self.__fakeFrameRate
			else:
				worldTime = self.timeInSeconds = wallTimeAtCall - self.t0
			# worldTime means seconds since the World's first rendered frame; it is used as an input to Animate methods and any property dynamics, and may be fake
		
			db = self.debugTiming
			db and self._DebugTiming( 'BeginFrameCallback' )
			if getattr( self, '_shady_stimuli', None ) is None or getattr( self, '_foreign_stimuli', None ) is None:
				self._SortStimuli(); db and self._DebugTiming( 'Separated' )
		
			# Shady stimuli will have already been rendered.
			# Now render foreign stimuli (e.g. pyglet sprites) if any
			foreign = self._foreign_stimuli
			if foreign:
				if self._accel: self._accel.DisableShadyPipeline()
				else: PyEngine.DisableShadyPipeline()
				for stimulus in foreign:
					try: draw = stimulus.draw
					except AttributeError: draw = stimulus.Draw
					try: draw()
					except:
						einfo = sys.exc_info()
						name = [ k for k, v in self.stimuli.items() if v is stimulus ][ 0 ]
						self.stimuli.pop( name, None )
						sys.stderr.write( 'Exception occurred while drawing foreign stimulus %r:\n' % name )
						self._excepthook( *einfo )
			db and self._DebugTiming( 'DrawForeignStimuli' )
		
			# Update managed properties of World and of Shady Stimulus objects
			self._Record( 'DrawTimeInMilliseconds', wallTimeAtCall, factor=1000.0 )
			self.Animate   and ( self._CallAnimate( worldTime ), db and self._DebugTiming( 'Animate' ) )
			self._dynamics and ( self._RunDynamics( worldTime ), db and self._DebugTiming( 'RunDynamics' ) )
			stimuli = self._shady_stimuli
			for stimulus in stimuli:
				stimulus.Animate   and ( stimulus._CallAnimate( worldTime - stimulus.t0 ), stimulus.debugTiming and stimulus._DebugTiming( 'Animate' ) )
				stimulus._dynamics and ( stimulus._RunDynamics( worldTime - stimulus.t0 ), stimulus.debugTiming and stimulus._DebugTiming( 'RunDynamics' ) )
			db and self._DebugTiming( 'DynamicsForAllStimuli' )
		
			# Run deferred tasks
			self._RunPending();     db and self._DebugTiming( 'RunPending' )
		
			# Clean up
			self._shady_stimuli = self._foreign_stimuli = None
		
			if hasattr( self.window, 'visible' ) and self.window.visible != self.visible:
				self.window.visible = self.visible = ( self.visible != 0 )
		
			#sys.stdout.write('*** leaving _FrameCallback ***\n'); sys.stdout.flush()
			return 0
	
	def _UniqueStimulusName( self, pattern=None ):
		if pattern is None: pattern = 'stim%02d'
		if '%' not in pattern:
			if pattern not in self.stimuli: return pattern
			pattern += '%02d'
		if not hasattr( self, 'nextStimulusNumber' ):
			self.nextStimulusNumber = 0
		while True:
			self.nextStimulusNumber += 1
			inflected = pattern % self.nextStimulusNumber
			if inflected not in self.stimuli: return inflected
				
	def _ComputeWorldNormalizer( self, width, height ):  # NB: never called if there's a DLL
		""" Converts pixel coordinates from lower left, to normalized [-1,+1] x [-1,+1]. """
		if self.__lastDims == ( width, height ): return  # No need to update matrix.
		self.__lastDims = ( width, height )
		self.matrixWorldNormalizer = [
			2.0 / width,  0.0,           0.0,     -1.0,
			0.0,          2.0 / height,  0.0,     -1.0,
			0.0,          0.0,           1.0,      0.0,   # TODO: could give more room to maneuver than -1 < z < 1  here by changing the 1.0 to, say, 2.0 / width
			0.0,          0.0,           0.0,      1.0,
		]		
		
	def _ComputeWorldProjection( self, ax, ay ):  # NB: never called if there's a DLL
		""" Orthographic. Applies world anchor. """		
		width, height = self.size
		if self.__lastAnchor == ( width, height, ax, ay ): return  # No need to update projection matrix.
		self.__lastAnchor = ( width, height, ax, ay )
		self.matrixWorldProjection = [
			1.0,          0.0,           0.0,      math.ceil( 0.5 * width  * ( ax + 1.0 ) ),
			0.0,          1.0,           0.0,      math.ceil( 0.5 * height * ( ay + 1.0 ) ),
			0.0,          0.0,           1.0,      0.0,
			0.0,          0.0,           0.0,      1.0,
		]

		
	@DeferredCall
	def Culling( self, enable, alphaThreshold=0.25 ):
		"""
		Depth culling is disabled by default. This means that where
		two stimuli overlap, every pixel is rendered in both stimuli.
		Depending on your stimulus arrangement, this may be a
		significant waste of resources.
		
		Turn culling on with `Culling( True )`.  Instead of drawing
		all pixels of all stimuli in furthest-to-nearest order (the
		painter's algorithm), Shady will now draw them in reverse
		painter's order, nearest-to-furthest, omitting calculations
		that would affect already-drawn-to pixels.
		
		Depth culling is fine if all your stimuli are opaque.
		The disadvantage to depth culling is that it affects alpha
		blending and composition: when a stimulus with some
		transparent parts is overlapped on another stimulus, depth
		culling alone would cause the `.clearColor` of the `World`
		to be drawn where there should be transparency.
		A partial countermeasure to this is alpha culling, which
		will be turned on concurrently with the depth test unless
		you explicitly specify a negative `alphaThreshold`. 
		With alpha culling, any pixel in any stimulus whose alpha is
		equal to or less than `alphaThreshold` is simply omitted,
		and stimuli behind it will show through at that point even
		with depth culling enabled.  The quality of some stimuli
		(e.g. antialiased text on a transparent background) will
		vary visibly depending on the threshold you choose, and
		will never be perfect.  Note also that semi-transparent
		pixels (where `alphaThreshold < alpha < 1.0`) may be
		rendered with inaccurate colors: stimulus colors get
		alpha-blended with the `.clearColor`, not with the
		colors of the stimuli behind them.
		
		
		Use `Culling( False )` to disable both depth and alpha
		culling.
		"""
		engine = self._accel
		if not engine: engine = PyEngine
		if enable: engine.EnableCulling( alphaThreshold )
		else: engine.DisableCulling()
		
	@DeferredCall
	def AddForeignStimulus(self, stimulus, name=None, z=0, **kwargs ):
		"""
		`stim` is either a class (or callable factory
		function) or an instance of a class.  That class
		should have a `.draw()` method. It is drawn on
		every frame with the Shady shader pipeline disabled
		(so, no automatic linearization or dithering, etc).
		
		The intention is to allow the use of one's own custom
		OpenGL primitives in drawing unusual stimuli.
		"""
		if callable( stimulus ): stimulus = stimulus( **kwargs )
		elif kwargs: [ setattr( stimulus, k, v ) for k, v in kwargs.items() ]
		stimulus.z = z
		stimulus.name = self._UniqueStimulusName(name)
		self.stimuli[ stimulus.name ] = stimulus
		return stimulus

	
	@DeferredCall
	def Wait( self ):
		"""
		Wait until after the next frame has been rendered. (Will have no
		effect, and return immediately, if your are calling this from the
		same thread in which your `World` runs.)
		"""
		return self.framesCompleted
	Tick = Wait
	
	@DeferredCall
	def LookupTable( self, *pargs, **kwargs ):
		"""Creates a `LookupTable` instance using `LookupTable( world=self, ... )`"""
		return LookupTable( self, *pargs, **kwargs )
		
	@DeferredCall
	def Stimulus( self, *pargs, **kwargs ):
		"""Creates a `Stimulus` instance using `Stimulus( world=self, ... )`"""
		return Stimulus( self, *pargs, **kwargs )
	
	@DeferredCall
	def Patch( self, **kwargs ):
		"""
		A convenience wrapper around the `.Stimulus()` method, for creating
		patches of solid color (supply `pp=1` for oval, `pp=-1` for rectangular).
		"""
		params = dict( name='patch%02d', color=1, bgalpha=0 )
		params.update( kwargs ); return Stimulus( self, **params )
	
	@DeferredCall
	def Sine( self, **kwargs ):
		"""
		A convenience wrapper around the `.Stimulus()` method, for creating
		a functionally-generated sine-wave patch, with the linearization
		and dynamic-range enhancement parameters ("atmosphere" parameters)
		yoked to those of the `World` by default.
		"""
		params = dict( name='sine%02d', signalFunction=1, signalAmplitude=min( min( self.bg ), min( 1.0 - x for x in self.bg ) ), atmosphere=self )
		params.update( kwargs ); return Stimulus( self, **params )
	
	@DeferredCall
	def MakeCanvas( self, **kwargs ):
		"""
		Create a `canvas` stimulus that covers the `World` and thereby allows
		the `World`'s `.backgroundColor`, `.gamma`, '.ditheringDenominator`
		and other "atmosphere" parameters to be put into effect.
		
		This is called automatically if you say `canvas=True` in your
		`World` constructor call.
		"""
		params = dict( name='canvas', source=None, useTexture=False, width=self.width, height=self.height, fg=-1, z=0.999 )
		params.update( kwargs )
		return Stimulus( self, **params ).LinkAtmosphereWithMaster( self ).LinkPropertiesWithMaster( self, 'outOfRangeColor outOfRangeAlpha anchor' ).Set( **kwargs )
		
	@DeferredCall
	def Close( self ):
		"""
		Close the `World`.
		"""
		self.__state = 'closing'
		self.window.Close()
		PyEngine.CleanUpGL()
		self.pstats = self.profile.stats()
		self.__state = 'closed'
		
	@DeferredCall
	def SetSwapInterval( self, value ):
		"""
		By default, Shady attempts to update the screen on every physical frame the
		display hardware can produce. This corresponds to a "swap interval" of 1 and
		on a typical modern LCD display this usually means 60 frames per second.
		If you set the swap interval to 2, updates will happen on every second frame
		(hence typically 30 fps) allowing you more time to perform computations
		between frames. 
		
		To synchronize frames with the hardware at all, Shady relies on the "vertical
		synch" option which may have to be enabled explicitly in the control panel
		of your graphics card driver. Without synchronization, you may observe
		"tearing" artifacts.
		
		The ability to change the swap interval is hit-and-miss, and back-end- and
		platform-dependent.  This call may have no effect.
		"""
		if self._accel: self._accel.SetSwapInterval( value, self.backend.lower().startswith( 'shadylib' ) )
		else: sys.stderr.write( 'SetSwapInterval(%r) ignored - cannot manipulate swap interval without using accelerator\n' % value )
			
	@DeferredCall
	def Capture( self, pil=False, fullscreen=False, saveas='', size=None, origin=None, normalize='auto' ):
		"""
		Takes a screenshot of the World and return the RGBA image data as a `numpy` array
		(`pil=False`) or as a `PIL.Image.Image` instance (`pil=True`).
		
		Args:
			pil (bool):
				If `True`,  and `PIL` or `pillow` is installed, an `Image` object is
				returned. Otherwise, return a `numpy` array (if `numpy` is installed) or
				a buffer containing the raw pixel information (if not).
			
			fullscreen (bool):
				Normally, with `fullscreen=False`, we capture just the `World` content.
				But if we specify `fullscreen=True`, and `PIL` or `pillow` is installed,
				and we're on Windows, then the `ImageGrab` module will be used to grab a
				shot of the whole screen as-is (including other windows and desktop
				content if the `World` fills only part of the screen or is partly
				obscured).
			
			saveas (str):
				If a filename is specified here, and `PIL` or `pillow` is installed, then
				the image is automatically saved under the specified filename.
			
			size (tuple, list):
				This is a sequence (tuple, list, or 1-D `numpy` array) containing 2
				integers: width and height, in pixels. If unspecified (`None`), the
				size of the `World` (`self.size`) is assumed.
			
			origin (tuple, list):
				This is a sequence (tuple, list, or 1-D `numpy` array) containing 2
				integers: x and y, in pixels, indicating the offset in pixels between the
				lower left corner of the `World` and the lower left corner of the capture
				are. If unspecified (`None`), `[0,0]` is assumed.
			
			normalize (bool or 'auto'):
				If `False`, return raw RGBA values as integers.
				If `True`, return floating-point values normalized in the range 0 to 1,
				and furthermore undo the effects of the current `.bitCombiningMode` if any.
				If `'auto'`, the default is `False` except when all the following conditions
				are met: `numpy` is installed, `pil` is `False`, and `self.bitCombiningMode`
				is non-zero.
		
		Returns:
			A `PIL.Image.Image` object (with `pil=True`, provided `PIL` or `pillow` is
			installed) or a `numpy` array (with `pil=False`) containing 8-bit RGBA pixel
			values.
		"""
		if normalize == 'auto':
			normalize = numpy and not pil and self.bitCombiningMode > 0
		elif normalize:
			if pil: raise ValueError( 'cannot combine `normalize=True` with `pil=True`' )
			if not numpy: raise ValueError( 'cannot use `normalize=True` because %s' %  numpy )
			if saveas: Announce( 'NB: image data returned from `.Capture()` will be normalized as requested, but saved image will not be' )
		if fullscreen:
			# NB: this does not appear to capture the foreground window if it is a 
			# pygame (i.e. SDL) window that is full-screen or de-facto-full-screen:
			# you will see the windows and desktop behind it, instead.
			if Image and not ImageGrab: raise ImportError( 'cannot capture with fullscreen=True because the PIL.ImageGrab module could not be imported - it may be that PIL does not implement ImageGrab on your platform' )
			img = ImageGrab.grab()
			if saveas: img.save( saveas )
			if pil: pass
			elif numpy: img = numpy.array( img )
			else: Announce( 'numpy unavailable - `.Capture()` will return a PIL image' )
		else:
			if size is None: size = self.size
			if not origin: origin = [ 0, 0 ]
			pixelScaling = [ original / float( current ) for original, current in zip( self.window.size, self.size ) ]
			# TODO: retina screens, when undetected by the pyglet backend, should multiply by a further factor of 2 here
			size   = [ int( round( x * s ) ) for x,s in zip( size,   pixelScaling ) ]
			origin = [ int( round( x * s ) ) for x,s in zip( origin, pixelScaling ) ]
			bytesPerPixel = 4
			if self._accel:
				buf = ctypes.create_string_buffer( size[ 0 ] * size[ 1 ] * bytesPerPixel )
				self._accel.CaptureRawRGBA( origin[ 0 ], origin[ 1 ], size[ 0 ], size[ 1 ], buf )
				rawRGBA = buf.raw # but NB: maybe shouldn't let the garbage collector get `buf` until the PIL image or numpy array has been created
			else:
				rawRGBA = PyEngine.CaptureRawRGBA( size, origin=origin )
			if not pil and not numpy:
				if Image: Announce( 'numpy unavailable - `.Capture()` will return a PIL image' ); pil = True
				else:     Announce( 'numpy unavailable - `.Capture()` will return raw bytes' )
			if pil or saveas:
				img = Image.frombuffer( 'RGBA', size, rawRGBA, 'raw', 'RGBA', 0, 1 ).transpose( Image.FLIP_TOP_BOTTOM )
				if saveas: img.save( saveas )
			if not pil:
				if numpy: img = numpy.fromstring( rawRGBA, dtype='uint8' ).reshape( [ size[ 1 ], size[ 0 ], 4 ] )[ ::-1, :, : ]
				else: img = rawRGBA
		if normalize:
			img = img.astype( float )
			if self.bitCombiningMode == 1:
				img[ :, :, 0 ] = img[ :, :, 1 ] = ( img[ :, :, 0 ] * 256.0 + img[ :, :, 1 ] ) / 65535.0
				img[ :, :, 2:4 ] /= 255.0
			elif self.bitCombiningMode == 2:
				img = ( img[ :, 0::2, : ] * 256.0 + img[ :, 1::2, : ] ) / 65535.0
				if self.pixelGrouping[ 1 ] == 2:
					if numpy.abs( img[ 0::2, :, : ] - img[ 1::2, :, : ] ).max():
						Announce( 'warning: despite .pixelGrouping[1] being equal to 2, odd rows of the `.Capture()` image are not identical to even rows' )
					img = img[ 0::2, :, : ]
			else:
				img /= self.dacMax
		return img
	
	@DeferredCall
	def CaptureToTexture( self, destTextureID, size=None, origin=None ):
		if size is None: size = self.size
		if not origin: origin = [ 0, 0 ]
		pixelScaling = [ original / float( current ) for original, current in zip( self.window.size, self.size ) ]
		# TODO: retina screens, when undetected by the pyglet backend, should multiply by a further factor of 2 here
		size   = [ int( x * s          ) for x, s in zip( size,   pixelScaling ) ]
		origin = [ int( round( x * s ) ) for x, s in zip( origin, pixelScaling ) ]
		if self._accel: return self._accel.CaptureToTexture( origin[ 0 ], origin[ 1 ], size[ 0 ], size[ 1 ], destTextureID )
		else: return PyEngine.CaptureToTexture( destTextureID, size=size, origin=origin )
	
	@call
	def bitCombiningMode():
		doc = """
		This non-managed property allows high-dynamic-range rendering on
		specialized vision-science hardware. It can be set to:
		
		0, or equivalently `'C24'`:
		    denotes standard 24-bit full-color mode (8 bits per channel,
		    with dithering by default).
		
		1, or equivalently `'M16`' or `'monoPlusPlus'`:
		    denotes 16-bit monochrome reinterpretation of frame-buffer
		    contents (each pixel's red channel is the more-significant byte,
		    and its green channel is the less-signficiant byte, of a 16 bit
		    value). As with look-up tables, Shady reads just the red channel
		    to determine the monochrome target value. Dithering is disabled.
			
		2, or equivalently `'C48'` or `'colorPlusPlus'`:
		    denotes 48-bit color mode in which horizontal resolution is
		    sacrificed. Dithering is disabled. Each pixel in the frame buffer
		    is paired with its horizontal neighbor, and together they specify
		    a 16-bit-per-channel value for the corresponding yoked pair of
		    physical pixels. Shady also throws away vertical resolution at
		    the same time, so that you can continue working with square
		    pixels and sane geometry---if you do not want this, then the
		    `.SetBitCombiningMode()` method allows more control.
			
		Values 3 and 4 are also reserved for debugging C48 mode (they will
		*not* generate correct C48 stimuli).
		"""
		def fget( self ): return self.pixelReinterpretation
		def fset( self, value ): self.SetBitCombiningMode( value )
		return property( fget=fget, fset=fset, doc=doc )
		
	def SetBitCombiningMode( self, mode, verticalGrouping='iso' ):
		"""
		This method supports high-dynamic-range rendering on specialized
		vision-science hardware---see documentation for the
		`.bitCombiningMode` property for full details.  Calling
		`w.SetBitCombiningMode(mode)` is the same as simply assigning
		`w.bitCombiningMode = mode`.  The only difference is that, when
		`mode=2` (sacrificing horizontal resolution to achieve 16-bit-per-
		channel full-color rendering), the method allows you to specify
		separately whether vertical resolution should also be sacrificed.
		Shady's default behavior is to throw away vertical resolution at
		the same time, so that logical pixels remain physically square,
		as follows::
		
		    w.SetBitCombiningMode( mode=2, verticalGrouping=2 )
		
		However you can override this, changing the aspect ratio of your
		pixels and retaining full vertical resolution, as follows::
		
		    w.SetBitCombiningMode( mode=2, verticalGrouping=1 )
		
		"""
		if mode is None: return
		if not isinstance( mode, str ) and hasattr( mode, 'mode' ): mode = mode.mode
		arg = mode
		if isinstance( mode, ( int, float ) ): mode = str( int( mode ) )
		mode = mode.lower()
		if mode.startswith( 'fake-' ): mode = mode[ 5: ]
		if   mode in [ 'normal', 'default', 'c24', '0' ]:
			self.size = self.window.size
			self.pixelGrouping = self.GetPropertyDescriptor( 'pixelGrouping' ).default
			self.pixelReinterpretation = 0
		elif mode in [ 'monoplusplus', 'mono++', 'm16', 'm14', '1' ]:
			self.size = self.window.size
			self.pixelGrouping = self.GetPropertyDescriptor( 'pixelGrouping' ).default
			self.pixelReinterpretation = 1
		elif mode in [ 'colourplusplus', 'colour++', 'colorplusplus', 'color++', 'c48', 'c42', '2', '3', '4' ]:
			if verticalGrouping == 'iso': verticalGrouping = 2
			self.pixelGrouping = [ 2, verticalGrouping ]
			self.size = [ int( round( size / float( grouping if grouping > 0.0 else 1.0 ) ) ) for size, grouping in zip( self.window.size, self.pixelGrouping ) ]
			try: mode = int( mode ) # 3 and 4 are distinct debugging modes in the shader
			except: mode = 2
			self.pixelReinterpretation = mode
		else:
			raise ValueError( "unrecognized bitCombiningMode value %r" % arg )
		return self
	
	def ReportVersions( self, outputType='print', importAll=False ):
		"""
		This method calls the global function `ReportVersions` with the `World`
		instance as its first argument.
		"""
		d = dict( self.versions ) # contains a frozen set of version info as at World creation (we do this because some things might have changed since then, like the back-end)
		if importAll:
			for k, v in ReportVersions( outputType='dict', importAll=importAll ).items():
				if k not in d: d[ k ] = v    # only add info if there's not already an entry
		if outputType == 'dict': return d
		s = '\n'.join( '%30r : %r,' % item for item in d.items() )
		if outputType == 'string': return s
		elif outputType == 'print': print( '\n' + s + '\n' )
		else: raise ValueError( 'unrecognized output type %r' % outputType )

@ClassWithManagedProperties._Organize
class Stimulus( LinkGL ):
	"""
	A `Stimulus` is an entity that is drawn automatically within its parent `World`
	on every frame. It has a number of properties whose values govern its appearance
	independent of other stimuli.
	
	Args:
		world (World):
			The required first argument is a `World` instance. To make this more readable
			you can alternatively call the `Stimulus` constructor as a `World` method::

				w = World( ... )
				s = w.Stimulus( source, ... )
		
		source (str, list, numpy.ndarray, None):
			The second argument is the `source` of the carrier texture. This may be
			omitted (or equivalently set to `None`) if your stimulus is just a blank
			patch, or if its carrier signal is defined purely by a function in the shader
			(see the `.signalFunction` property).  Alternatively `source` may be a string
			denoting an image filename or glob pattern for image filenames, a `numpy`
			array specifying texture data explicitly, or a list of strings and/or
			`numpy` arrays - see `.LoadTexture()` for details.
		
		name (str):
			This is a string that will identify this `Stimulus` in the container
			`w.stimuli` of the `World` to which it belongs. To ensure uniqueness of the
			names in this `dict`, you may include a single numeric printf-style pattern in
			the name (the default `name`, for example, is `'stim%02d'`).
		
		page (int):
			You may optionally initialize the `.page` property here.
		
		multipage (bool):
			If you set this to `True`, multiple image frames will loaded using the
			`.LoadPages()` method: this transfers each frame to the graphics card as a
			separate texture, which you switch between using the `.page` property.
			
			By contrast, if you leave it at the default value `False`, multiple image
			frames are handled by concatenating them horizontally into a single texture,
			and you switch between them using the `.frame` property, which indirectly
			manipulates `.carrierTranslation`.
			
			You may need to use `multipage=True` for animated images that have a large
			width and/or high number of frames, because the normal concatenation method
			may lead to the texture exceeding the maximum allowable width.
		
		**kwargs:
			Managed property values can also be specified as optional keyword arguments
			during construction---for example::
			
				s = w.Stimulus( ..., foregroundColor=[1, 0, 0], ... )
			
			The `width`, `height` and/or `size` arguments (all shortcuts/aliases into
			the `.envelopeSize` managed property) are worth mentioning specifically: these
			can be used to specify the dimensions of the envelope in pixels. For texture
			stimuli these can usually be omitted, since usually they will be dictated by
			the dimensions of the underlying `source` material. However, they can be
			specified explicitly if you want to crop or repeat an image texture. Note that
			you should specify dimensions in the same units as the underlying texture
			(i.e. *unscaled* pixels). If you want to change the physical size of the
			rendered stimulus by magnifying or shrinking the texture, manipulate the
			`.envelopeScaling` property either directly, or indirectly via `.scaledSize`
			(but remember this will produce interpolation artifacts).
	"""

	def __init__( self, world, source=None, name=None, page=None, multipage=False, debugTiming=None, **kwargs ):
		if not isinstance( world, World ): raise TypeError( 'first argument must be a World instance---maybe you intended to use the .Stimulus() method of a World instance but said Shady.Stimulus(...) instead?' )
		self.world = weakref.ref( world )
		self._Construct( world=world, source=source, name=name, page=page, multipage=multipage, debugTiming=debugTiming, **kwargs )

	@DeferredCall
	def _Construct( self, world, source=None, name=None, page=None, multipage=False, debugTiming=None, **kwargs ):

		self.name = world._UniqueStimulusName( name )
		if world._accel: self._accel = self._Accelerate( world._accel.CreateStimulus( self.name ) )
		else:            self._accel = None
		self._Initialize( world, debugTiming )
		self.serialNumber = len( world.stimuli )
		world.stimuli[ self.name ] = self
		self.t0 = 0.0  # "world Time"
		self.__page = None
		self.__linearMagnification = True
		self.pages = {}
		self.source = None
		if isinstance( source, Stimulus ): self.Inherit( source )
		if source is None:
			# store width and height for future reference, if specified here
			self.Set( **kwargs )
			if 'textureSize' not in kwargs: self.textureSize = self.envelopeSize
		elif multipage:
			self.LoadPages( source, page=page if page else 0, **kwargs )
		else:
			self.NewPage( source, key=page, **kwargs )
		if not self._accel:
			PyEngine.InitQuad( self, legacy=world._legacy ) # Buffers initial vertex data (depends only on envelopeSize) and creates VAO
	
	
	@DeferredCall
	def LoadPages( self, sources, keys=0, updateEnvelopeSize=True, page=0, **kwargs ):
		"""
		This method prepares a `Stimulus` instance for animation using the
		`.page` mechanism (rather than the default `.frame` mechanism).		
		It loads multiple textures in multiple pages, indexed by the
		specified `keys` (or by integers starting at `keys`, if `keys`
		is an integer). Subsequently, you can switch between pages by
		setting the `.page` property or equivalently calling the
		`.SwitchTo()` method.
		
		This method is called when constructing a `Stimulus` instance
		with the `multipage` constructor option.  It can also be called
		explicitly, which is especially useful if you want to re-use
		texture buffers that have already been allocated on the graphics
		card, for new stimulus content.		
		"""
		sources = AsImageFrames( sources )
		if isinstance( keys, int ):
			keys = list( range( keys, keys + len( sources ) ) )
		for key, source in zip( keys, sources ):
			if key in self.pages:
				self.SwitchTo( key )
				self.LoadTexture( source, updateEnvelopeSize=False )
				if updateEnvelopeSize:
					self.Set( **kwargs )
					self.DefineEnvelope( -1, -1 )
					self.SavePage( self.__page )
				self.Set( **kwargs ) # before *and* after DefineEnvelope: avoids some problems with scaledSize, scaledWidth, scaledHeight
			else:
				self.NewPage( source, key=key, updateEnvelopeSize=updateEnvelopeSize, **kwargs )
		if page is not None: self.page = page
		
	@DeferredCall
	def Enter( self, **props ):
		"""
		If a `Stimulus` instance has previously left the stage with `.Leave()`,
		the `.Enter()` method allows it to come back.
		
		You may simultaneously change its properties, using keyword arguments.
		"""
		world = self.world()
		stimuli = world.stimuli
		if stimuli.get( self.name, self ) is not self: raise KeyError( "name %r is already taken in %r" % ( self.name, world ) )
		stimuli[ self.name ] = self
		for child in self._scheduled: child.world = world
		if self._accel: self._accel.Enter()
		if props: self.Set( **props )
		return self

	@DeferredCall
	def Leave( self, deferAfterAdditionalFrames=0 ):
		"""
		If a `Stimulus` instance `stim` is made invisible with `stim.visible=False`,
		it is not rendered on screen. However, it is still a member of the `.stimuli`
		dictionary of the `World` to which it belongs, and its `AnimationCallback`
		(if any), and any dynamics attached to its individual properties, are still
		evaluated on every frame.
		
		On the other hand, you tell a `Stimulus` instance to `.Leave()` the stage
		entirely, it is removed from the `.stimuli` dictionary of its `World`, it is
		not rendered (regardless of its `.visible` setting), and none of its
		callbacks and dynamics are called---not until you tell it to `.Enter()` again.
		
		Returns:
			the `Stimulus` instance itself.
		"""
		if deferAfterAdditionalFrames:
			defer = self.world().Defer
			args = [ defer ] * ( deferAfterAdditionalFrames - 1 ) + [ self.Leave ]
			defer( *args )
			return self
			
		self.world().stimuli.pop( self.name, None )
		for child in self._scheduled: child.world = None
		if self._accel: self._accel.Leave()
		return self

	def __del__( self ):
		pass # Announce( 'deleting %s' % self._Description() ) # TODO: this never happens - circular refs?
		# TODO: some way of recycling world slots...

	# Begin managed properties ############################################################
	textureSlotNumber__ = slot = ManagedProperty( -1, transfer='glUniformTextureSlot' )
	textureID                  = ManagedProperty( -1, transfer='glBindTexture_IfNotNegative' )

	envelopeSize__ = size = ( width, height ) = ManagedProperty(
		default = [ 200, 200 ],
		transfer = 'glUniform2f',
		doc = """
			This is a sequence of two numbers denoting the *unscaled* width and height of the envelope (i.e. width and height
			in texel units).  Change these numbers if, for example, you want to crop or repeat a texture, or to load new
			differently-shaped texture (the easiest way to do the latter is to call `.LoadTexture()` method with argument
			`updateEnvelopeSize=True`). To change the size of the envelope by stretching the image content to fit,
			manipulate `.envelopeScaling` or `.scaledSize` instead.
		""",
	)
	textureChannels = ManagedProperty(
		default = -1,
		transfer = 'glUniform1i',
		doc = """
			This is an integer value denoting whether the texture has 1, 2, 3 or 4 channels. If there is no texture, the
			value is -1.  You should consider this property read-only---do not change the value by hand.
		""",
	)
	textureSize = ManagedProperty(
		default = [ -1, -1 ],
		transfer = 'glUniform2f',
		doc = """
			This is a pair of values denoting the width and height of the texture data, in pixels. If there is no
			texture, both values are -1. You should consider this property read-only---do not change the values by hand.
		""",
	)
	visible__ = on = ManagedProperty(
		default = 1,
		doc = "This is a boolean value that determines whether the `{cls}` is rendered or not.",
	)

	z__ = depthPlane = depth = ManagedProperty(
		default = 0.0,
		doc = """
			This is a floating-point number that determines the depth plane of the `{cls}`.
			The convention is that negative values put you closer to the camera, and positive
			further away; also, you must ensure -1 <= z <= +1. Since the projection is orthographic,
			the value is purely used for depth-sorting of stimuli: therefore,
			setting `.z` to a non-integer value will not cause interpolation artifacts.
		""",
	)

	envelopeTranslation__ = envelopePosition = position = pos = xy = ( x, y ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'self._ComputeEnvelopeTranslation',
		doc = """
			This is a pair of numbers, expressed in pixels. It dictates the two-dimensional coordinates
			of the `{cls}` location within the drawing area.  The values are rounded down to integer values
			when they are applied, to avoid artifacts that might otherwise be introduced inadvertently
			due to linear interpolation during rendering.
			
			See also: `.envelopeOrigin`
		""",
	)
	envelopeOrigin = ( ox, oy, oz ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		doc = """
			This is a triplet of numbers, expressed in pixels, denoting the starting-point, in the coordinate system of the parent `World`,
			of the offsets `.envelopeTranslation` (which is composed of `.x` and `.y`) and depth coordinate `.z`.
			The actual rendered position of the anchor point of `{cls}` `s` will be::
			
				[ int(s.x) + s.ox,   int(s.y) + s.oy,  s.z + s.oz ]
			
			relative to the `World`'s own `.origin`.
			
			You can manipulate `.envelopeOrigin` exclusively and leave `.envelopeTranslation` at 0, as an alternative
			way of specifying `{cls}` position. This is the way to go if you prefer to work in 3D floating-point coordinates
			instead of 2D integers: unlike `.envelopeTranslation`, this property gives you the opportunity to represent non-integer
			coordinate values. With that flexibility comes a caveat: non-whole-number values of `.ox` and `.oy` may result in artifacts in any kind of `{cls}`
			(textured or not) due to linear interpolation during rendering.  You may therefore wish to take care to round
			any values you assign, if you choose to use this property.  If you exclusively use `.envelopeTranslation` instead,
			this pitfall is avoided (as you can see in the formula above, its components `.x` and `.y` are rounded down to
			integer values when they are applied).
			
			Note also that for all stimuli,
			you should ensure that the total depth coordinate, `s.z + s.oz`, is in the range ( -1, +1 ].
		""",
	)
	envelopeRotation__ = rotation = orientation = angle = ManagedProperty(
		default = 0.0,
		transfer = 'self._ComputeEnvelopeRotation',
		doc = """
			This is a scalar number, expressed in degrees. The envelope will be rotated counter-clockwise
			by this number of degrees around its `.anchor`. Note that such transformations of the envelope
			(except at multiples of 90 degrees) will introduce small artifacts into any stimulus, due to linear interpolation.
		""",
	)
	envelopeScaling__ = scale = ( xscale__, yscale__ ) = scaling = ( xscaling__, yscaling__ ) = ManagedProperty(
		default = [ 1.0, 1.0 ],
		transfer = 'self._ComputeEnvelopeScaling',
		doc = """
			This is a sequence of two floating-point numbers denoting horizontal and vertical scaling factors.
			The actual rendered size, in pixels, of the scaled `{cls}` `s` will be `s.envelopeScaling * s.envelopeSize`
			Note that such transformations of the envelope will introduce small artifacts into any stimulus, due to linear interpolation.
		""",
	)
	anchor = ( ax_n__, ay_n__ ) = ( anchor_x, anchor_y ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'self._ComputeAnchorTranslation',
		doc = """
			This is a sequence of two floating-point numbers expressed in normalized coordinates (from -1 to +1).
			It denotes where, on the surface of the envelope, the anchor point will be.  This anchor point is the point
			whose coordinates are manipulated directly by the other properties, and it also serves as the origin of any scaling
			and rotation of the envelope. The default value is `[0.0, 0.0]` denoting the center, whereas
			`[-1.0, -1.0]` would be the bottom left corner.
			
			The translation caused by changes to `.anchor` is always rounded down to an integer number of pixels,
			to avoid it becoming an unforeseen cause of interpolation artifacts.
		""",
	)
	matrixAnchorTranslation = ManagedProperty( IDENTITY4FV, transfer = 'glUniformTransformation4' )
	#matrixEnvelopeTricks = ManagedProperty( IDENTITY4FV, transfer = 'glUniformTransformation4' )
	matrixEnvelopeScaling = ManagedProperty( IDENTITY4FV, transfer = 'glUniformTransformation4' )
	matrixEnvelopeRotation = ManagedProperty( IDENTITY4FV, transfer = 'glUniformTransformation4' )
	matrixEnvelopeTranslation = ManagedProperty( IDENTITY4FV, transfer = 'glUniformTransformation4' )

	useTexture = ManagedProperty(
		default = 1,
		transfer = 'glUniform1i',
		doc = """
			This is a boolean value. The default value is `True` if a texture has been specified,
			and this causes pixel values to be drawn from the texture specified by the constructor argument
			`source` (or the `source` argument to a subsequent `.NewPage()` or
			`.LoadTexture()` call).  If `.useTexture` is set to `False`, the pixel
			values are determined by `.backgroundColor` and/or `.foregroundColor`
			(as well as `.offset`, `.normalizedContrast`, and any windowing and
			shader-side `.signalFunction` or `.modulationFunction`).
		""",
	)
	carrierRotation__ = cr = ManagedProperty(
		default = 0.0,
		doc = """
			This is a scalar number, expressed in degrees. The carrier will be rotated counter-clockwise
			by this number of degrees around the center of the envelope. 
			Note that if your rotation values is not divisible by 90, this will introduce interpolation artifacts
			into stimuli that use textures. (Unlike `.envelopeRotation`, however, this will not compromise
			pure functionally-generated stimuli.)
		""",
	)
	carrierScaling__ = cscale = ( cxscale__, cyscale__ ) = cscaling = ( cxscaling, cyscaling ) = ManagedProperty(
		default = [ 1.0, 1.0 ],
		doc = """
			This is a sequence of two floating-point numbers denoting horizontal and vertical scaling factors.
			The carrier will be magnified by these factors relative to an origin the center of the envelope.
			Note that scaling values != 1.0 will introduce interpolation artifacts into stimuli that use textures
			(but unlike `.envelopeScaling`, this will not compromise pure functionally-generated stimuli).
		""",
	)
	carrierTranslation = ( cx, cy ) = ManagedProperty(
		default = [ 0.0, 0.0 ],
		transfer = 'self._ComputeCarrierTransformation',
		doc = """
			This is a sequence of two numbers, expressed in pixels, corresponding to x and y dimensions.
			It shifts the carrier (texture stimulus and/or shader function) relative to the envelope.
			Note that non-integer translation values will introduce interpolation artifacts into stimuli that
			use textures (but unlike `.envelopeTranslation`, this should not compromise pure functionally-generated stimuli).
		""",
	)
	carrierTransformation = ManagedProperty( IDENTITY3FV, transfer = 'glUniformTransformation3' )

	offset = ( addr, addg, addb ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0.0 to 1.0, corresponding to red, green and blue channels. 
			This is added uniformly to all pixel values before they are scaled by `.normalizedContrast` or by
			windowing (via `.plateauProportion` and `.windowingFunction`) and/or custom modulation (via `.modulationFunction`).
		""",
	)
	normalizedContrast__ = contrast = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a scalar floating-point value in the range 0.0 to 1.0
			which scales the overall contrast of the `{cls}`. At a contrast of 0,
			the `{cls}` is reduced to its `.backgroundColor`.
		""",
	)
	plateauProportion__ = pp = ( ppx, ppy ) = ManagedProperty(
		default = [ -1.0, -1.0 ],
		transfer = 'glUniform2f',
		doc = """
			This is sequence of two floating-point values corresponding to the x and y dimensions.
			
			A negative value indicates that no windowing is to be performed in the
			corresponding dimension.
			
			A value in the range [0, 1] causes windowing to occur: with the default
			(raised cosine) `.windowingFunction`, a `.plateauProportion` of 0 gives
			a Hann window, 1 gives a boxcar window, and intermediate
			values combine the specified amount of constant plateau with a raised-
			cosine falloff to the edge of the envelope (i.e., a Tukey window).
			
			A non-zero plateau proportion can also be combined with other (custom
			self-written) `.windowingFunction` implementations.
			
			Note that this means [1, 1] gives a circular or elliptical envelope with
			sharp edges, in contrast to [-1, -1] which gives a square or rectangular envelope.
		""",
	)
	signalFunction__ = sigfunc = ManagedProperty(
		default = 0,
		transfer = 'glUniform1i',
		doc = """
			This is an integer specifying the index of a shader-side signal function.
			If it is left at 0, no function is used: the carrier content is then dependent
			purely on the texture, if any, or is blank if no texture was specified. 
		
			A value of 1 (which can also be referenced as the constant `SIGFUNC.SinewaveSignal`)
			corresponds to the one and only shader-side signal function that we provide out of
			the box, namely  `SinewaveSignal` which generates a sinusoid.  The parameters of the
			sinusoid are determined by the `.signalParameters` property.
			
			Further values, and hence further functions, may be supported if you add them yourself
			using `AddCustomSignalFunction()`.
			
			In the shader, the return value of a signal functions is either
			a `vec3` or a `float`. This return value gets multiplied by the `.color` of the `{cls}`,
			and added to its `.backgroundColor` (and/or its texture, if any).  If `.color` is
			negative (i.e. disabled, as it is by default) then the function output is multiplied by
			`vec3(1.0, 1.0, 1.0)`.  
			
			See also: `.signalParameters`, `.modulationFunction`, `.modulationParameters`, `.windowingFunction`
		""",
	)
	signalParameters__ = ( signalAmplitude__, signalFrequency__, signalOrientation__, signalPhase__ ) = ( siga, sigf, sigo, sigp ) = ManagedProperty(
		default = [ 1.0, 0.05, 0.0, 0.0 ],
		transfer = 'glUniform4f',
		doc = """
			This is a 4-element vector that can be used to pass parameters to the shader-side
			carrier-signal-generating function chosen by `.signalFunction`.
			If `.signalFunction` is left at its default value of 0, the `.signalParameters`
			are ignored. For the one built-in shader signal function (`.signalFunction=1`
			corresponding to the shader function `SinewaveSignal`), these parameters
			are interpreted as amplitude, frequency, orientation and phase of the
			sinusoidal pattern.  Signal functions are additive to your background and/or texture,
			so if you have no texture and a background color of, for example, 0.3 or 0.7,
			a sinewave amplitude greater than 0.3 will go out of range at full contrast. (Beware also the
			additive effect of noise, if your `.noiseAmplitude` is not 0.)
			
			If you're adding your own custom shader function via `AddCustomSignalFunction()`, your
			implementation of that function may choose to ignore or reinterpret this property
			as you wish. If you choose to use it, your shader code can access it as the
			uniform `vec4` variable  `uSignalParameters.`
			
			See also: `.signalFunction`, `.modulationFunction`, `.modulationParameters`
		""",
		notes = "amplitude from 0 to 1; frequency in cycles/pixel; orientation in degrees; phase in degrees",
	)
	modulationFunction__ = modfunc = ManagedProperty(
		default = 0,
		transfer = 'glUniform1i',
		doc = """
			This is an integer specifying the index of a shader-side contrast modulation function.
			If it is left at 0, no function is used: the stimulus contrast is then dependent
			only on the overall `.normalizedContrast` and on the window applied according to
			`.plateauProportion`.
			
			A value of 1 (which can also be referenced as the constant `MODFUNC.SinewaveModulation`)
			corresponds to the one and only shader-side modulation function that we provide out of
			the box, namely  `SinewaveModulation` which performs sinusoidal contrast modulation.
			The parameters of this modulation pattern are determined by the `.modulationParameters` property.
			
			Further values, and hence further functions, may be supported if you add them yourself
			using `AddCustomModulationFunction()`.
			
			In the shader, the return value of a modulation
			function is a `float`. This return value is used as a multiplier for stimulus contrast. 
			
			See also: `.modulationParameters`, `.signalFunction`, `.signalParameters`, `.windowingFunction`
		""",
	)
	modulationParameters__ = ( modulationDepth__, modulationFrequency__, modulationOrientation__, modulationPhase__ ) = ( modd, modf, modo, modp ) = ManagedProperty(
		default = [ 0.0, 0.005, 0.0, 90.0 ],
		transfer = 'glUniform4f',
		doc = """
			This is a 4-element vector that can be used to pass parameters to the shader-side
			contrast-modulation function chosen by `.modulationFunction`.
			
			If `.modulationFunction` is left at its default value of 0, these four values
			are ignored. For the one built-in shader modulation function (`.modulationFunction=1`
			corresponding to the shader function `SinewaveModulation`), the values
			are interpreted as depth, frequency, orientation and phase of the desired sinusoidal
			modulation pattern.
			
			If you're adding your own custom shader function via `AddCustomModulationFunction()`, your
			implementation of that function may choose to ignore or reinterpret this
			property as you wish. If you choose to use it, your shader code can access it as the
			uniform `vec4` variable  `uModulationParameters.`
			
			See also: `.modulationFunction`, `.signalFunction`, `.signalParameters`
		""",
		notes = "amplitude, i.e. modulation depth, from 0 to 1; frequency in cycles/pixel; orientation in degrees; phase in degrees",
	)
	modulationAmplitude = moda = modulationDepth__
	windowingFunction__ = windowFunction = winfunc = ManagedProperty(
		default = 1,
		transfer = 'glUniform1i',
		doc = """
			This is an integer specifying the index of a shader-side windowing function.
			If it is set to 0 (or if the `.plateauProportion` property is negative), no
			spatial windowing is used.
			
			The default value of 1 (which can also be referenced as the constant `WINFUNC.Hann`)
			corresponds to the one and only shader-side windowing function that we provide out of
			the box, namely  `Hann`, which causes contrast to fall off according to a
			raised cosine function of radial distance.
			
			Further values, and hence further functions, may be supported if you add them yourself
			using `AddCustomWindowingFunction()`.
			
			In the shader, the windowing function takes one
			input argument (a `float` whose value will range from 0 at peak of the window to 1 at
			the edge) and return a `float`. This return value is used as a multiplier for stimulus
			contrast.
			
			See also: `.signalFunction`, `.modulationFunction`
		""",
	)
	backgroundAlpha__ = bgalpha = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a floating-point number from 0 to 1, indicating the opacity at locations where the
			signal has been attenuated away completely (by windowing via `.plateauProportion`, by a custom
			`.modulationFunction`, or by manipulation of overall `.normalizedContrast`).
			
			For psychophysical stimuli, ensure `.backgroundAlpha` is 1.0 and manipulate `.backgroundColor` instead:
			although alpha *can* be used for windowing in this way, alpha-blending is applied post-linearization
			so the result will not be well linearized, except in very fragile special cases.
		""",
	)
	backgroundColor__ = bgcolor = bg = ( bgred, bggreen, bgblue ) = ManagedProperty(
		default = [ 0.5, 0.5, 0.5 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels. It
			specifies the color at locations in which the carrier signal (texture and/or foreground color and/or
			functionally generated carrier signal) has been attenuated away completely (by contrast scaling, windowing,
			or custom contrast modulation pattern).
		""",
	)
	noiseAmplitude__ = noise = ( rednoise, greennoise, bluenoise ) = ManagedProperty(
		default = [ 0.0, 0.0, 0.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of floating-point numbers corresponding to red, green and blue channels.
			Negative values lead to uniform noise in the range `[s.noiseAmplitude[i], -s.noiseAmplitude[i]]`.
			Positive values lead to Gaussian noise with standard deviation equal to the `.noiseAmplitude` value.
			
			The noise specified in this way is applied before gamma-correction, and is monochromatic (i.e.
			perfectly correlated across color channels, though it may have different amplitudes in each channel).
			It is particularly useful for applying very-low-amplitude noise prior to look-up in a high-dynamic-range
			bit-stealing look-up table. It can also be useful at higher amplitudes, to create visible noise effects.
			
			It is not to be confused with noisy-bit dithering, which is applied post-gamma-correction (and
			only when a look-up table is not used), and which is controlled independently by the
			`.ditheringDenominator` property.
		""",
	)
	gamma = ( redgamma, greengamma, bluegamma ) = ManagedProperty(
		default = [ 1.0, 1.0, 1.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of values denoting the screen gamma that
			should be corrected-for in each of the red, green and blue channels.
			A gamma value of 1 corresponds to the assumption that your
			screen is already linear.  Setting gamma values other than 1
			is an alternative to using a pre-linearized lookup-table or `.lut`.
			
			Any value less than or equal to 0.0 is interpreted to denote
			the sRGB function, which is a standard piecewise function that
			follows the `gamma=2.2` curve quite closely (although the exponent
			it uses is actually slightly higher).
			
			Note that `gamma` is ignored for stimuli that use a `.lut`
		""",
	)
	ditheringDenominator__ = dd = ManagedProperty(
		default = 0.0,
		default_string = 'dithering enabled (value determined automatically)',
		transfer = 'glUniform1f',
		doc = """
			This is a floating-point number. It should be 0 or negative to disable dithering, or otherwise
			equal to the maximum DAC value (255 for most video cards). It allows implementation of the
			"noisy-bit" dithering approach (Allard & Faubert, 2008) for increasing effective dynamic range.
			
			This is distinct from the `.noiseAmplitude` property, which specifies noise that is (a) applied
			pre-gamma-correction, (b) can be scaled differently in different color channels, but (c) is
			otherwise perfectly correlated across color channels.   Noisy-bit dithering, on the other hand
			(a) is applied post-gamma-correction, (b) has the same amplitude in all color channels but
			(c) is indepdent in each color channel.
			
			Note that, like gamma-correction, noisy-bit dithering is disabled for stimuli that use a `.lut`
			
		""",
	)
	color__ = ( red__, green__, blue__ ) = foregroundColor = fgcolor = fg = ( fgred, fggreen, fgblue ) = ManagedProperty(
		default = [ -1.0, -1.0, -1.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels. Values
			may also be negative, in which case no colorization is applied in the corresponding channel.
			
			Where non-negative, foreground color plays slightly different roles depending on other parameters:
			
			If the `{cls}` uses a texture, the pixel values from the texture are tinted via multiplication with the `.color` values.
			
			If the `{cls}` uses a `.signalFunction` then the signal is also multiplied by the `.color` before being added.
			
			If there is no texture and no `.signalFunction`, the carrier image consists of just the specified uniform solid `.color`.
			The `{cls}` color may still be attenuated towards the `.backgroundColor`---uniformly by
			setting `.normalizedContrast` < 1.0, and/or as a function of space by setting `.plateauProportion` `>= 0.0` or
			by using a `.modulationFunction`).
		""",
	)
	alpha__ = fgalpha = opacity = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a floating-point number from 0 to 1. It specifies the opacity of the `{cls}` as a whole.
			Note that with psychophysical stimuli you should always ensure `.alpha` == 1, and manipulate
			`.backgroundColor` and '.normalizedContrast` instead: this is because alpha-blending is carried
			out by the graphics card AFTER our linearization (via the `.gamma` property or via a look-up table)
			is applied. Therefore a blended result will no longer be linearized.
		""",
	)
	outOfRangeColor = ManagedProperty(
		default = [ 1.0, 0.0, 1.0 ],
		transfer = 'glUniform3f',
		doc = """
			This is a triplet of numbers, each in the range 0 to 1, corresponding to red, green and blue channels.
			It specifies the color that should be used for pixels whose values go out of range. A negative value
			means "do not flag out-of-range values in this color channel" (values are merely clipped in the
			range 0 to 1 in that case).
		""",
	)
	outOfRangeAlpha = ManagedProperty(
		default = 1.0,
		transfer = 'glUniform1f',
		doc = """
			This is a floating-point number from 0 to 1.
			It specifies the color that should be used for pixels whose values go out of range.
			A negative value disables this feature (the alpha value of an out-of-range pixel is left unchanged).
		""",
	)
	debugDigitsStartXY = ManagedProperty( [ -1.0, -1.0 ], transfer='glUniform2f' )
	debugDigitSize     = ManagedProperty( [ -1.0, -1.0 ], transfer='glUniform2f' )
	debugValueIJK = ( dbi, dbj, dbk ) = ManagedProperty( [ 0.0, 0.0, 0.0 ], transfer='glUniform3f' )
	lookupTableTextureSize = ManagedProperty( [ -1, -1, -1, -1 ], transfer='glUniform4f' )
	lookupTableTextureSlotNumber = ManagedProperty( -1, transfer='glUniformTextureSlot' )
	lookupTableTextureID = ManagedProperty( -1, transfer='glBindTexture_IfNotNegative' )
	penThickness = ManagedProperty(
		default = 1.0,
		doc = """
			This is a scalar floating-point value that determines the width, in pixels, of
			of lines and points drawn when you set `.drawMode` to `DRAWMODE.POINTS`,
			`DRAWMODE.LINES`, `DRAWMODE.LINE_STRIP` or `DRAWMODE.LINE_LOOP`.
			Implementation is driver-dependent however: many graphics cards seem to consider
			line-thickness to be a legacy feature and have dropped support for it (for lines,
			but maybe not for points) in their pure modern-OpenGL contexts.
		""",
	)
	smoothing = ManagedProperty(
		default = 1,
		doc = """
			This is an integer value that determines whether lines, dots and polygons should
			be drawn with or without smoothing.  The results are unfortunately unpredictable
			as they vary according to your graphics card and drivers. Example: with
			`DRAWMODE.POINTS`, setting `.smoothing=1` causes the dots to be round rather
			than square---but with some graphics drivers, they will remain square regardless
			(to guarantee round dots, it's better to draw tiny many-sided polygons).
			A value of 0 means no smoothing. A value of 1 means points and lines should
			be smoothed.  A value of 2 means lines, points and polygons are smoothed (note
			that polygon smoothing causes diagonal "crack" artifacts on many graphics
			cards/drivers, so this option is not enabled by default).
		""",
	)
	pointsXY = ManagedProperty( default = [ 0.0 ] * MAX_POINTS * 2 )
	nPoints__ = numberOfPoints = npoints = ManagedProperty( default = 0 )
	drawMode = ManagedProperty(
		default = 1,
		transfer = 'self._DrawShapes',
		doc = """
			This is an integer that selects between different drawing behaviors. The different
			values are given meaningful names in the namespace `DRAWMODE`, whose documentation
			also explains the behavior of the different draw modes.
		""",
	)
	# NB: drawMode should be the last ManagedProperty in this sequence
	# End managed properties ############################################################

	@call
	def points():
		doc = """
		This is a view into the `Stimulus` instance's optional array of coordinates.
		If you do not have the third-party package `numpy` installed, then this is fairly
		limited (although you can assign a list of alternating x and y coordinates to it,
		you will not be able to do any array arithmetic operations with it, which is where
		its power lies).  With `numpy`, your `.points` will appear as an `n`-by-2 array
		of coordinates (you can also view the same data as a sequence of complex numbers,
		by accessing as `.pointsComplex`).  These coordinates are not used in the
		default `.drawMode`, which is `DRAWMODE.QUAD`.  To learn how other draw modes
		use the coordinates, see the documentation for the `DRAWMODE` namespace.
		
		Assignment to `.points` is interchangeable with assignment to `.pointsComplex`---in
		either case, the input can be a sequence of `n` complex numbers OR an `n`-by-2 array
		of real-valued coordinates.  Under the hood, assignment to `.points` changes the
		content of the managed property `.pointsXY` and also adjusts the managed property
		`.nPoints`
		
		The coordinate system of the `.points` is always in pixels relative to the
		bottom-left corner of the `Stimulus` bounding-box---i.e. the bottom-left corner
		of the rectangle you would see if you were to switch the `Stimulus` back to
		`drawMode=Shady.DRAWMODE.QUAD`.  The `World.anchor`, `Stimulus.position`,
		`Stimulus.anchor` and `Stimulus.size` determine where this local origin actually
		lies on screen, but the `.points` themselves are expressed independently of these, 
		and points defined outside the bounding-box (e.g. with negative coordinates) still
		get drawn.
		"""
		def fget( self ):
			if numpy: n = self.nPoints; return self.pointsXY[ :n * 2 ].reshape( [ n, 2 ] )
			else: return self.pointsXY
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'points', value, order=2.0, canonicalized=True )
			self.SetDynamic( 'points', None, canonicalized=True )
			if numpy:
				if not isinstance( value, numpy.ndarray ): value = numpy.array( value )
				if numpy.iscomplexobj( value ): value = numpy.c_[ value.real.flat, value.imag.flat ]
				self.nPoints = value.size // 2
				self.pointsXY.flat[ :value.size ] = value.flat
			else:
				try: value[ 0 ][ 0 ]
				except: 
					try: value[ 0 ].imag
					except: pass
					else: value = [ x for z in value for x in ( z.real, z.imag ) ]
				else: value = [ x for pair in value for x in pair ]
				self.nPoints = len( value ) // 2
				if value: self.pointsXY[ :len( value ) ] = value
		return property( fget=fget, fset=fset, doc=doc )	
				
	@call
	def pointsComplex():
		doc = """
		This is a view into the `Stimulus` instance's optional array of coordinates. The
		same data are also accessible as `.points`.  The only difference is that when you ask for
		`.pointsComplex`, the data are interpreted as a sequence of complex numbers (requires
		the third-party package `numpy`).
		
		Assignment to `.pointsComplex` is interchangeable with assignment to `.points`---in
		either case, the input can be a sequence of `n` complex numbers OR an `n`-by-2 array
		of real-valued coordinates. 
		"""
		def fget( self ):
			dtype = numpy.complex128 # raises an exception if numpy is not installed
			return self.pointsXY[ : self.nPoints * 2 ].view( dtype )
		def fset( self, value ): self.points = value
		return property( fget=fget, fset=fset, doc=doc )
			
	def _DrawShapes( self, mode ):  # NB: never called if there's a DLL
		if not mode: return
		mode_lookup = getattr( self, '_drawmode_lookup', None )
		if mode_lookup is None: self._drawmode_lookup = mode_lookup = { v : [ k, None, None, None ] for k, v in DRAWMODE.__dict__.items() if not k.startswith( '_' ) }
		PyEngine.DrawShapes( mode_lookup[ mode ], self )

	@call
	def page():
		doc = """
			A `Stimulus` may optionally have more than one "page".  A page is
			a label attached to a particular set of property values that
			determine texture, envelope size and envelope shape.
			
			A page may have any hashable label---integers and strings are
			usually the most meaningful. The `.page` property allows you to
			query the label of the current page, or switch to a different
			page according to its label.  It is not a managed property, but
			it does support dynamic value assignment.
						
			See also: `.LoadPages()`, `.NewPage()`, `.SavePage()`, and `.SwitchTo()`
		"""
		def fget( self ):
			return self.__page
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'page', value, order=2.0, canonicalized=True )
			self.SetDynamic( 'page', None, canonicalized=True )
			if isinstance( value, float ) and value not in self.pages: value = int( value )
			if isinstance( value, int ) and value not in self.pages: value %= len( self.pages )
			if isinstance( value, int ) and value not in self.pages: value = list( self.pages.keys() )[ value ]
			self.SwitchTo( value )
		return property( fget=fget, fset=fset, doc=doc )

	@call
	def frame(): # pseudo-ManagedProperty (in that it supports _RunDynamics)
		doc = """
			This non-managed property is an integer denoting the index of the
			current frame of a multi-frame stimulus. Note that frames are
			concatenated horizontally in the underlying carrier texture, so a
			change in `.frame` is actually achieved by manipulating `.cx`,
			otherwise known as `.carrierTranslation[0]`.
		"""
		def fget( self ):
			if not self.textureSize[ 0 ] or not self.envelopeSize[ 0 ]: return 0
			try: frameWidth = self.frameWidth
			except: frameWidth = self.envelopeSize[ 0 ]
			return ( -self.carrierTranslation[ 0 ] % self.textureSize[ 0 ] ) // frameWidth
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'frame', value, order=2.1, canonicalized=True )
			self.SetDynamic( 'frame', None, canonicalized=True )
			try: frameWidth = self.frameWidth
			except: frameWidth = self.envelopeSize[ 0 ]
			self.carrierTranslation[ 0 ] = int( ( -frameWidth * int( value ) ) % self.textureSize[ 0 ] )
		return property( fget=fget, fset=fset, doc=doc )

	@property
	def nFrames( self ):
		"""
		Read-only non-managed property that returns the width of each frame,
		if the texture pixel data is divided up horizontally into multiple frames.
		"""
		try: frameWidth = self.frameWidth
		except: frameWidth = self.envelopeSize[ 0 ]
		return self.textureSize[ 0 ] // frameWidth


	@call
	def scaledSize():
		doc="""
		Non-managed property that reflects the product of `.envelopeSize` and `.envelopeScaling`.
		Assigning to this property will change `.envelopeScaling` accordingly. Dynamic value
		assignment is supported.  Note that you can also address `.scaledWidth` and
		`.scaledHeight` separately if you wish.
		"""
		def fget( self ): return ( self.scaledWidth, self.scaledHeight )
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'scaledSize', value, order=2.2, canonicalized=True )
			self.SetDynamic( 'scaledSize', None, canonicalized=True )
			try: w, h = value
			except: w = h = value
			self.scaledWidth, self.scaledHeight = w, h
		return property( fget=fget, fset=fset, doc=doc )
	@call
	def scaledWidth():
		doc="""
		Non-managed property that reflects the product of `.envelopeSize[0]` and `.envelopeScaling[0]`.
		Assigning to this property will change `.envelopeScaling[0]` accordingly. Dynamic value
		assignment is supported.
		"""
		def fget( self ): return self.envelopeSize[ 0 ] * self.envelopeScaling[ 0 ]
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'scaledWidth', value, order=3.0, canonicalized=True )
			self.SetDynamic( 'scaledWidth', None, canonicalized=True )
			if self.envelopeSize[ 0 ]: self.envelopeScaling[ 0 ] = float( value ) / self.envelopeSize[ 0 ]
		return property( fget=fget, fset=fset, doc=doc )
	@call
	def scaledHeight():
		doc="""
		Non-managed property that reflects the product of `.envelopeSize[1]` and `.envelopeScaling[1]`.
		Assigning to this property will change `.envelopeScaling[1]` accordingly. Dynamic value
		assignment is supported.
		"""
		def fget( self ): return self.envelopeSize[ 1 ] * self.envelopeScaling[ 1 ]
		def fset( self, value ):
			if callable( value ): return self.SetDynamic( 'scaledHeight', value, order=3.0, canonicalized=True )
			self.SetDynamic( 'scaledHeight', None, canonicalized=True )
			if self.envelopeSize[ 1 ]: self.envelopeScaling[ 1 ] = float( value ) / self.envelopeSize[ 1 ]
		return property( fget=fget, fset=fset, doc=doc )

	def _ComputeAnchorTranslation( self, ax, ay ):  # NB: never called if there's a DLL
		""" Compute final translation values from envelope translation, size, anchor, and origin. """
		width, height = self.envelopeSize
		tx = PartialTranslation( -width, ax )
		ty = PartialTranslation( -height, ay )
		self.matrixAnchorTranslation = [
			1.0, 0.0, 0.0, tx,
			0.0, 1.0, 0.0, ty,
			0.0, 0.0, 1.0, 0.0,
			0.0, 0.0, 0.0, 1.0,
		]

	def _ComputeEnvelopeScaling( self, sx, sy ):  # NB: never called if there's a DLL
		""" Compute final scale (no Z-scaling). """
		self.matrixEnvelopeScaling = [
			sx,  0.0, 0.0, 0.0,
			0.0, sy,  0.0, 0.0,
			0.0, 0.0, 1.0, 0.0,
			0.0, 0.0, 0.0, 1.0,
		]

	def _ComputeEnvelopeRotation( self, rz ):  # NB: never called if there's a DLL
		""" Compute final rotation (simple for Shady stimuli, as only Z-rotation is used). """
		rz = math.radians( rz )
		cos_rz = math.cos( rz )
		sin_rz = math.sin( rz )
		self.matrixEnvelopeRotation = [
			+cos_rz, -sin_rz, 0.0, 0.0,
			+sin_rz, +cos_rz, 0.0, 0.0,
			0.0,     0.0,     1.0, 0.0,
			0.0,     0.0,     0.0, 1.0,
		]

	def _ComputeEnvelopeTranslation( self, tx, ty ):  # NB: never called if there's a DLL
		""" Compute final translation values from envelope translation, size, anchor, and origin. """
		try: tx = math.floor( tx )
		except: pass
		try: ty = math.floor( ty )
		except: pass
		ox, oy, oz= self.envelopeOrigin
		self.matrixEnvelopeTranslation = [
			1.0, 0.0, 0.0, tx + ox,
			0.0, 1.0, 0.0, ty + oy,
			0.0, 0.0, 1.0, self.z + oz,
			0.0, 0.0, 0.0, 1.0,
		]

	def _ComputeCarrierTransformation( self, cx, cy ):  # NB: never called if there's a DLL
		alpha = -self.carrierRotation * math.pi / 180.0
		cos_a, sin_a = math.cos( alpha ), math.sin( alpha )
		x_scale, y_scale = self.carrierScaling
		x_origin, y_origin = [ x / 2.0 + c for x, c in zip( self.envelopeSize, ( cx, cy ) ) ]
		x_shift = -cos_a * x_origin / x_scale + sin_a * y_origin / x_scale + x_origin - cx
		y_shift = -cos_a * y_origin / y_scale - sin_a * x_origin / y_scale + y_origin - cy
		self.carrierTransformation = [
			+cos_a / x_scale,    -sin_a / y_scale,    x_shift,
			+sin_a / y_scale,    +cos_a / y_scale,    y_shift,
			0.0,                 0.0,                 1.0,
		]

	def ResetClock( self, other=None ):
		"""
		A `Stimulus` may have callback functions that are called on every
		frame---for example, a function that you have registered as its
		`AnimationCallback`, or functions that you assign to its managed
		properties (dynamic value assignment).  In all cases, the argument
		that is passed to these callbacks on each frame is `t`, time in
		seconds.  By default, this `t` is the same as the `World`'s `.t`,
		i.e. the number of seconds have elapsed since the `World` began
		rendering. However, if you wish, you can alter the `.t0` from which
		each `Stimulus` instance's clock counts::
		
			stim.ResetClock()            # resets the clock to 0
			stim.ResetClock( otherStim ) # synchronizes with `otherStim`
		
		"""
		if other: self.t0 = getattr( other, 't0', other )
		else: self.t0 = self.world().t	
	
	def Capture( self, pil=False, saveas='', normalize='auto' ):
		"""
		This captures the pixel data from a particular `Stimulus`.  Note that it
		accomplishes this simply by calling `World.Capture()` with the appropriate
		bounding box.  Therefore, two caveats:  (1) if other stimuli overlap this
		one, the capture will contain image data composited from all of them;
		(2) the bounding- box method is smart enough to compensate for
		`.envelopeTranslation` and `.envelopeScaling`, but not `.envelopeRotation`.
		
		Args:
			pil (bool):
				If `True`, and if `PIL` or `pillow` is installed, return the image data
				as a `PIL.Image.Image` instance.   If `False`, return the data as a
				`numpy` array.
			
			saveas (str):
				If `PIL` or `pillow` is installed, you can use this argument to specify
				an optional filename for immediately saving the image data.
		
			normalize (bool or 'auto'):
				If `False`, return raw RGBA values as integers.
				If `True`, return floating-point values normalized in the range 0 to 1,
				and furthermore undo the effects of the current `.bitCombiningMode` if any.
				If `'auto'`, the default is `False` except when all the following conditions
				are met: `numpy` is installed, `pil` is `False`, and `self.bitCombiningMode`
				is non-zero.
			
		Returns:
			Either a `numpy.ndarray` or a `PIL.Image.Image` instance, depending on the
			`pil` argument.
		"""
		origin, size = self.BoundingBox()
		return self.world().Capture( pil=pil, saveas=saveas, fullscreen=False, size=size, origin=origin, normalize=normalize )

	def CaptureToTexture( self, destTextureID ):
		origin, size = self.BoundingBox()
		return self.world().CaptureToTexture( destTextureID=destTextureID, size=size, origin=origin )

	def BoundingBox( self, worldCoordinates=False ):
		"""
		This method returns the bounding box of the `Stimulus`, in pixels.
		
		Args:
			worldCoordinates (bool):
				If `True`, then the `left` and `bottom` coordinates are computed relative
				to the `World`'s `.anchor`. If `False`, then `[0,0]` is considered to be
				the bottom-left corner of the `World`, regardless of its `.anchor`.
		
		Returns:
			`[left, bottom], [width, height]` pixel coordinates for the `Stimulus`.
		
		Known Issues:
			The method takes account of scaling (due to `.envelopeScaling`) and
			translation (due to `.envelopeOrigin`, `.envelopeTranslation`,
			`Stimulus.anchor` and `World.anchor`). But it does *not* take account of
			`.envelopeRotation`
		"""
		# TODO: really should recreate *all* envelope transformations including envelopeRotation...
		world = self.world()
		bottomLeft = [
			  self.envelopeOrigin[ i ]
			+ self.envelopeTranslation[ i ]
			- ( 0 if worldCoordinates else PartialTranslation( -world.size[ i ], world.anchor[ i ] ) )
			+ PartialTranslation( -self.scaledSize[ i ], self.anchor[ i ] )
		for i in range( 2 ) ]
		size = self.scaledSize[ :2 ]
		return list( bottomLeft ), list( size )

	def DefineEnvelope( self, width=None, height=None ):
		if width is None:  width  = self.envelopeSize[ 0 ]
		if height is None: height = self.envelopeSize[ 1 ]
		if width  < 0: width  = getattr( self, 'frameWidth', -1 )
		if width  < 0: width  = self.textureSize[ 0 ]
		if height < 0: height = self.textureSize[ 1 ]
		self.envelopeSize = width, height

	@DeferredCall
	def NewPage( self, source, key=None, updateEnvelopeSize=True, **kwargs ):
		"""
		Create a new page from the specified `source`. A page is a
		bundle of properties that determine texture, envelope size,
		and (via `.drawMode` and `.points`) envelope shape.
		
		Note that this can be automated, to load multiple sources
		as multiple pages, either by specifying `multipage=True` when
		you construct the `Stimulus` instance, or by explicitly
		calling `.LoadPages()`.
		
		Args:
			
			source
				Any valid input to `.LoadTexture()`, including `None`.
			
			key
				By default, a new page is unlabelled, but if you specify
				a `key` here, `.SavePage( key )` will be called
				automatically to store and label the new texture settings.
				This will enable you to `.SwitchTo()` this page in future.
			
			**kwargs
				Additional keyword arguments can be used to set property
				values at the same time, if you want. (NB: you can set
				any property at all this way, but remember that not all
				properties get paged in and out---apart from the ones whose
				values get inferred from `source` automatically, the others
				that are most meaningful here are `.drawMode` and `.points`)
		
		See also: `.page`, `.SavePage()`, `.SwitchTo()` and `.LoadPages()`
		"""
		self.drawMode = DRAWMODE.QUAD
		self.nPoints = 0
		self.textureSlotNumber = -1 
		self.textureID = -1
		self.envelopeSize = -1
		self.LoadTexture( source, False ) # this is the only part that actually *needs* to be deferred, but we'll defer the whole of NewPage so that the lines above are also delayed and the visual changes don't come out of sync
		if updateEnvelopeSize:
			self.Set( **kwargs )
			self.DefineEnvelope( -1, -1 )
		self.Set( **kwargs ) # before *and* after DefineEnvelope: avoids some problems with scaledSize, scaledWidth, scaledHeight
		#if not -1.0 <= self.z <= 1.0: raise ValueError( "z must be in the range [-1, 1]" )
		if key is not None: self.SavePage( key )
	
	def SavePage( self, key ):
		"""
		Save the current "page" (a bundle of properties determining texture,
		envelope size and envelope shape) in the dictionary `self.pages` under
		the specified `key`.
		
		See also: `.page`, `.NewPage()`, and `.SwitchTo()`
		"""
		fields = 'useTexture textureSlotNumber textureID textureSize envelopeSize frameWidth drawMode points'.split()
		self.pages[ key ] = { k : getattr( self, k ) * 1 for k in fields }
		self.__page = key
	
	def SwitchTo( self, key ):
		"""
		Switch to the "page" associated with the given `key`.  A page is a
		bundle of properties that determine texture, envelope size and
		envelope shape.  The `key` argument must be one of the keys in the
		dictionary `self.pages`.   Note that if the current settings have
		not been stored (via `.SavePage()`, via the explicit specification
		of a key during `.NewPage()`, or via the automated loop of
		`.NewPage()` calls provided by `.LoadPages()`) then this method
		will cause the current settings to be lost.
		
		See also: `.page`, `.NewPage()`, `.LoadPages()` and `.SavePage()`
		"""
		for k, v in self.pages[ key ].items(): setattr( self, k, v )
		self.__page = key
		return key

	@DeferredCall
	def AddDebugDigits( self, value=None, x=0, y=0, i=0, j=0, k=0 ):
		nDigits = 10
		imageFileName = PackagePath( 'glsl/digits_small.png' )
		if not Image: raise ImportError( 'cannot load %r: Image module not available (need to install `PIL` or `pillow` package)' % imageFileName )
		if not numpy: raise ImportError( 'cannot manipulate image pixels unless you install the `numpy` package' )
		digits = numpy.array( Image.open( imageFileName ), dtype=float ) / 255.0
		digits[ :, :, 3 ] = 1.0
		img = numpy.array( self.source, copy=True ) # could add digits with LoadSubTexture instead of relying on self.source...
		while img.ndim < 3: img = numpy.expand_dims( img, -1 )
		self.debugValueIJK = [ i, j, k ]
		self.debugDigitsStartXY = [ x, y ]
		digitWidth, digitHeight = self.debugDigitSize = [ digits.shape[ 1 ] // nDigits, digits.shape[ 0 ] ]
		rStart = img.shape[ 0 ] - y - digitHeight
		img[ rStart : rStart + digitHeight, x : x + digitWidth * nDigits, : ] = digits[ :, :, :img.shape[ 2 ] ]
		if value is not None: img[ i, j, k ] = value # ...but then we could not do this, in only one channel, with LoadSubTexture...
		self.LoadTexture( img ) # ...so let's just load the whole texture back in
		return self

	@DeferredCall
	def LoadTexture( self, source, updateEnvelopeSize=True, useTexture=True ):
		"""
		Loads texture data from `source` and associates it with this Stimulus.
		
		Args:
			source:  the source of the carrier texture data. This may be:
			
				- omitted or set to `None` if there is no texture (just a constant carrier
				  signal, or one defined by a function in the shader)
				
				- a string (possibly including glob characters `'*'` and/or `'?'`) denoting one
				  or more image files to be used as animation frames
				
				- a `numpy` array specifying the pixel values of a texture image, in which case:
				
					- `source.dtype` must be one of:
					   - `numpy.dtype('uint8')`   : 8-bit pixel values in the range 0 to 255
					   - `numpy.dtype('float32')` : pixel value in the range 0.0 to 1.0
					   - `numpy.dtype('float64')` : pixel value in the range 0.0 to 1.0
					     (will be converted to float32 automatically)
					
					- `source.shape` must be one of:
						- `[height, width]`        : LUMINANCE image
						- `[height, width, 1]`     : LUMINANCE image
						- `[height, width, 2]`     : LUMINANCE_ALPHA image
						- `[height, width, 3]`     : RGB image
						- `[height, width, 4]`     : RGBA image
				
				- a `list` or `tuple` containing filenames and/or `numpy` arrays as above, to be
				  used as multiple frames
			
			updateEnvelopeSize (bool): whether or not to update the envelope size to match the
			                           dimensions of the new texture
			
			useTexture (bool): new value for the `.useTexture` property attribute that
			                   enables or disables the use of this texture
		"""
		
		if isinstance( source, Stimulus ):
			for key in 'textureID textureSlotNumber textureSize source frameWidth'.split(): setattr( self, key, getattr( source, key ) )
			if updateEnvelopeSize: self.envelopeSize = self.frameWidth, self.textureSize[ 1 ]
			return self

		sourceList = AsImageFrames( source )
		
		if len( sourceList ) == 0:
			source = None
		elif len( sourceList ) == 1:
			source = sourceList[ 0 ]
			self.frameWidth = source.shape[ 1 ]
		else:
			self.frameWidth = max( source.shape[ 1 ] for source in sourceList )
			frameHeight = max( source.shape[ 0 ] for source in sourceList )
			channels = max( source.shape[ 2 ] for source in sourceList )
			strip = numpy.zeros( [ frameHeight, self.frameWidth * len( sourceList ), channels ], dtype=sourceList[ 0 ].dtype )
			# TODO: we're limited by MAX_TEXTURE_EXTENT (see above) so the texture will fail to transfer
			#       if you have, say, more than 32 frames of a 500-by-N-pixel image on the Surface Pro 3
			#       or more than 16 frames of the same image on the MacBook11,1
			for i, source in enumerate( sourceList ):
				xoffset = i * self.frameWidth + ( self.frameWidth - source.shape[ 1 ] ) // 2
				yoffset = ( frameHeight - source.shape[ 0 ] ) // 2
				strip[ yoffset : yoffset + source.shape[ 0 ], xoffset : xoffset + source.shape[ 1 ], : ] = source
				# TODO: will fail if frames differ in their number of channels
			source = strip
		self.source = source # TODO: might need to omit this to save memory
		if source is None: return self
		# at this point we can assume a 3-D numpy array (height by width by channels)
		
		if useTexture is not None: self.useTexture = useTexture
		self.textureSize = [ source.shape[ 1 ], source.shape[ 0 ] ]
		if updateEnvelopeSize: self.envelopeSize = self.frameWidth, self.textureSize[ 1 ]
		prepped = PrepareTextureData( source )
		self.textureChannels = prepped[ 2 ]
		if self._accel:
			self._accel.LoadTexture( *prepped )
		else:
			if self.textureSlotNumber < 0: self.textureSlotNumber = 0
			self.textureID = PyEngine.LoadTexture( self.textureSlotNumber, self.textureID, *PrepareTextureData( source ) )
		self.linearMagnification = self.linearMagnification # side-effect of property setter ensures this preference is configured in the appropriate place

	@DeferredCall
	def LoadSubTexture( self, source, x=0, y=0 ):
		"""
		This is similar to `.LoadTexture()` in its interpretation of the
		`source` argument. The difference is that the `Stimulus` must
		already have an existing texture, and the new source is pasted
		over the old one (or over part of it, depending on the new
		source's size).
		
		`x` and `y` are pixel coordinates relative to the existing
		texture's lower-left corner. They specify the position of the
		lower-left corner of the incoming piece of the texture.
		"""
		# note: x<0 and y<0 does not wrap around, array-like;  it just moves the edge of the subtexture out of bounds and hence truncates the subtexture
		if self.textureID < 0: raise TypeError( 'cannot load a subtexture into a Stimulus that has no texture' )
		if isinstance( source, basestring ):
			if not Image: raise ImportError( 'cannot load textures from file unless you install the `PIL` or `pillow` package' )
			source = Image.open( source )
		if not numpy: raise ImportError( 'cannot manipulate textures unless you install the `numpy` package' )
		if not isinstance( source, numpy.ndarray ): source = numpy.array( source )
		if source.ndim == 1: source = source[ :, None ]
		if source.ndim == 2: source = source[ :, :, None ]
		canvasWidth, canvasHeight = self.textureSize 
		brushHeight, brushWidth = source.shape[ :2 ]
		column, row = x, canvasHeight - y - brushHeight
		if row < 0: source = source[ -row:, :, : ]; row = 0
		if row + brushHeight > canvasHeight: source = source[ :canvasHeight - row - brushHeight, :, : ]
		if column < 0: source = source[ :, -column:, : ]; column = 0
		if column + brushWidth > canvasWidth: source = source[ :, :canvasWidth - column - brushWidth, : ]
		if not source.size: return
		prepped = PrepareTextureData( source )
		if prepped[ 2 ] != self.textureChannels: raise ValueError( 'sub-texture array must have the same number of channels as the original texture (%d)' % self.textureChannels )
		if self._accel: self._accel.LoadSubTexture( column, row, *prepped )
		else:           PyEngine.LoadSubTexture( self.textureSlotNumber, self.textureID, column, row, *prepped )
	
	@call
	def linearMagnification():
		doc = """
		This property governs the interpolation behavior applied when a textured
		`Stimulus` is enlarged (i.e. when its `.envelopeScaling` or `.carrierScaling`
		are greater than 1).
		
		If `True` (default), interpolate pixel values linearly when enlarged.
		
		If `False`, take the "nearest pixel" method when enlarged.
		"""
		def fget( self ): return self.__linearMagnification
		def fset( self, value ): self.__linearMagnification = ( self._accel.SetLinearMagnification( value ) if self._accel else PyEngine.SetLinearMagnification( self.textureID, value ) )
		return property( fget=fget, fset=DeferredCall( fset ), doc=doc )
			
	def ShareTexture( self, *others ):
		"""
		This is a wrapper around `.ShareProperties()` that allows `Stimulus`
		instances to share a texture---it shares the `textureID`, `textureSlotNumber`,
		`textureSize` and `useTexture` managed properties.
		"""
		return self.ShareProperties( 'textureID textureSlotNumber useTexture textureSize', *others )
	
	def LinkTextureWithMaster( self, master ):
		"""
		This is a wrapper around `.LinkPropertiesWithMaster()` that allows `Stimulus`
		instances to share a texture---it shares the `textureID`, `textureSlotNumber`
		and `useTexture` managed properties.
		"""
		master.ShareTexture( self )
		return self
		
def StubProperty( cls, name, requirement ):
	instruction = 'To use the `.%s` property of the `%s` class, you must first %s' % ( name, cls.__name__, requirement )
	def fail( self, value=None ): raise AttributeError( instruction )
	setattr( cls, name, property( fget=lambda self: None, fset=fail, doc=instruction ) )
StubProperty( Stimulus, 'text',  'explicitly `import Shady.Text` (see `Shady.Text` for documentation on this property).' )
StubProperty( Stimulus, 'video', 'explicitly `import Shady.Video` (see `Shady.Video` for documentation on this property).' )

def PrepareTextureData( sourceArray, *pargs ):
	if sourceArray.dtype == 'float64':
		sourceArray = sourceArray.astype( 'float32' )
	elif sourceArray.dtype != 'uint8' and sourceArray.dtype.name.startswith( ( 'int', 'uint' ) ) and sourceArray.min() >= 0 and sourceArray.max() <= 255:
		sourceArray = sourceArray.astype( 'uint8' )
	if sourceArray.dtype not in [ 'float32', 'uint8' ]: raise TypeError( 'unsupported data type %r' % sourceArray.dtype.name )
	width     = sourceArray.shape[ 1 ] if len( sourceArray.shape ) >= 2 else 1
	height    = sourceArray.shape[ 0 ]
	nChannels = sourceArray.shape[ 2 ] if len( sourceArray.shape ) >= 3 else 1
	dataType  = sourceArray.dtype.name
	data      = sourceArray.tostring( order='C' )
	return ( width, height, nChannels, dataType, data ) + pargs

ALL_LOOKUPTABLES = {}
@ClassWithManagedProperties._Organize
class LookupTable( LinkGL ):
	"""
	Class that encapsulates the properties of a look-up table.
	
	A `LookupTable` has a small number of managed properties which are not directly
	transferred to the GPU.  Under the hood, they work by being *shared* with
	`Stimulus` instances (see `.ShareProperties()` )
	"""
	def __init__( self, world, values ):
		"""
		You probably will not need to call this constructor directly. It is implicitly
		called when you assign to the `.lut` property of a `Stimulus` instance or,
		equivalently, call the `Stimulus` instance's `.SetLUT()` method.
		
		Args:
			world (World):
				a `World` instance
			
			values (str, list, numpy.ndarray):
				Any valid input to `Shady.Linearization.LoadLUT()`.
		
		See also:
			- `Stimulus.SetLUT()`
		"""
		self.world = weakref.ref( world )
		self._Construct( world=world, values=values )
		
	@DeferredCall
	def _Construct( self, world, values ):
		if world._accel: self._accel = self._Accelerate( world._accel.CreateRGBTable() )
		else:            self._accel = None
		self._Initialize( world, debugTiming=False )
		self.LoadValues( values )

	length = property( lambda self: max( 0, self.lookupTableTextureSize[ 2 ] ) )
	
	@DeferredCall
	def LoadValues( self, values ):
		values = LoadLUT( values )
		length = values.size // values.shape[ -1 ]
		
		# juggle dimensions to fit within maximum allowed width and/or height of GL texture
		height, width = length, 1
		target_width = 1
		extra = 0
		while height > MAX_TEXTURE_EXTENT:
			target_width *= 2
			height = length // target_width
			width = int( math.ceil( length / float( height ) ) )
			extra = width * height - length
		if extra:
			extra = numpy.zeros_like( values[ :extra, :, : ] )
			values = numpy.concatenate( [ values, extra ], axis=0 )
		self.values = values
		nChannels = values.shape[ 2 ]
		textureData = values.reshape( [ width, height, nChannels ] ).transpose( [ 1, 0, 2 ] )
		
		self.lookupTableTextureSize = [ textureData.shape[ 1 ], textureData.shape[ 0 ], length, nChannels ]
		if self._accel:
			self._accel.LoadTexture( *PrepareTextureData( textureData ) )
		else:
			if self.lookupTableTextureSlotNumber < 0: self.lookupTableTextureSlotNumber = 1
			self.lookupTableTextureID = PyEngine.LoadTexture( self.lookupTableTextureSlotNumber, self.lookupTableTextureID, *PrepareTextureData( textureData, True ) )
		
		keys = [ key for key, ref in ALL_LOOKUPTABLES.items() if ref() is self ]
		for key in keys: ALL_LOOKUPTABLES.pop( key, None )
		key = tuple( self.lookupTableTextureSize ) + ( self.lookupTableTextureSlotNumber, self.lookupTableTextureID )
		ALL_LOOKUPTABLES[ key ] = weakref.ref( self )
		
		
	# Begin managed properties ############################################################
	lookupTableTextureSize = ManagedProperty( [ -1, -1, -1, -1 ] ) # no transfer function - just share
	lookupTableTextureSlotNumber__ = slot = ManagedProperty( -1 )  #  these properties with whichever
	lookupTableTextureID = ManagedProperty( -1 )                   #  Stimulus objects want to use the LUT
	# End managed properties ############################################################
	
class Scheduled( object ):
	
	__deferred = []
	__world = None
	__parent = None
	__selfref = None
	__cancel = False
	priority = 0
	
	
	@classmethod
	def _MakeProperty( cls, name, *otherNames ):
		def fget( self ): return self._Property( name )
		def fset( self, value ): self._Property( name, value )
		prop = property( fget=fget, fset=fset )
		allNames = ( name, ) + otherNames
		for eachName in allNames: setattr( cls, eachName, prop )
		if not hasattr( cls, '_propertyNames' ): cls._propertyNames = []
		cls._propertyNames.append( '='.join( allNames ) )
		return prop
		
	def _Property( self, optionName, newValue=None ):
		pass
		
	def _Update( self ):	
		pass
		
	def _TryUpdate( self ):
		cancel, self.__cancel = self.__cancel, False
		if cancel: return
		self.ScheduleUpdate()
		try:
			self._Update()
		except:
			einfo = sys.exc_info()
			world = self.world
			if not world: reraise( *einfo )
			getattr( world, '_excepthook', sys.excepthook )( *einfo )
			self.CancelUpdate()
			
	@staticmethod
	def _WeakTryUpdate( ref ):
		self = ref()
		if self is not None: return self._TryUpdate()
		
	def ScheduleUpdate( self ):
		world = self.world
		self.__cancel = False
		if self.__selfref is None: self.__selfref = weakref.ref( self )
		if world: self.__deferred = world.Defer( ( self.priority, self._WeakTryUpdate ), self.__selfref )
		
	def CancelUpdate( self ):
		world = self.world
		self.__cancel = True
		if world: world.Undefer( self.__deferred )
		
	@call
	def world():
		def fget( self ): value = self.__world; return value() if isinstance( value, weakref.ReferenceType ) else value
		def fset( self, value ):
			self.CancelUpdate()
			if value is not None and not isinstance( value, weakref.ReferenceType ): value = weakref.ref( value )
			if value is not None and value() is None: value = None
			self.__world = value
			self.ScheduleUpdate()
		return property( fget=fget, fset=fset )
		
	@call
	def parent():
		def fget( self ): value = self.__parent; return value() if isinstance( value, weakref.ReferenceType ) else value
		def fset( self, value ):
			if value is not None and not isinstance( value, weakref.ReferenceType ): value = weakref.ref( value )
			if value is not None and value() is None: value = None
			if self.__parent:  self.__parent()._scheduled.pop( self, None )
			if value: value()._scheduled[ self ] = 1
			self.__parent = value
			self.world = value().world if value else None
		return property( fget=fget, fset=fset )
	
	def Set( self, **kwargs ):
		for k, v in kwargs.items(): setattr( self, k, v )
		return self	
	#Set = ClassWithManagedProperties.Set   # why no worky on Python 2?

	@classmethod
	def _AttachAsProperty( guestClass, hostClass, parentPropertyName, redirectedSubpropertyName=None, attachSubproperties=True, onRemove=None, onWorldClose=None ):
		hiddenName = '_' + parentPropertyName
		def fget( host ): return getattr( host, hiddenName, None )
		def fset( host, value ):
			guest = getattr( host, hiddenName, None )
			if value is None or isinstance( value, guestClass ):
				if guest:
					guest.CancelUpdate()
					if onRemove:
						def Remove( wrHost, wrGuest ):
							host, guest = wrHost(), wrGuest()
							host and guest and onRemove( host, guest )
						host.world().Defer( Remove, weakref.ref( host ), weakref.ref( guest ) )
				host.SetDynamic( parentPropertyName, None, canonicalized=True )
				setattr( host, hiddenName, value )
				if value: value.stimulus = host
			elif redirectedSubpropertyName:
				if guest is None:
					guest = guestClass( stimulus=host )
					setattr( host, hiddenName, guest )
				if callable( value ): return host.SetDynamic( parentPropertyName, value, order=2.0, canonicalized=True )
				host.SetDynamic( parentPropertyName, None, canonicalized=True )
				setattr( guest, redirectedSubpropertyName, value )	
			else:
				raise TypeError( '.%s property expects instance of type %s' % ( parentPropertyName, guestClass.__name__ ) )
			if guest and onWorldClose:
				def Cleanup( wrGuest ): guest = wrGuest(); guest and onWorldClose( guest )
				host.world().OnClose( Cleanup, weakref.ref( guest ) )
		setattr( hostClass, parentPropertyName, property( fget=fget, fset=fset ) )			
		if attachSubproperties: guestClass._AttachSubproperties( hostClass, parentPropertyName )

	@classmethod
	def _AttachSubproperties( guestClass, hostClass, parentPropertyName ):
		def Attach( subpropertyName, *otherNames ):
			fullName = parentPropertyName + '_' + subpropertyName
			def fget( host ): return getattr( getattr( host, parentPropertyName, None ), subpropertyName )
			def fset( host, value ):
				guest = getattr( host, parentPropertyName, None )
				if not guest: return # TODO: or raise exception?
				if callable( value ): return host.SetDynamic( fullName, value, order=3.0, canonicalized=True )
				host.SetDynamic( fullName, None, canonicalized=True )
				setattr( guest, subpropertyName, value )
			prop = property( fget=fget, fset=fset )
			for alias in ( subpropertyName, ) + otherNames:
				setattr( hostClass, parentPropertyName + '_' + alias, prop )
		for subpropertyName in getattr( guestClass, '_propertyNames', [] ):
			Attach( *subpropertyName.split( '=' ) )

class Chronicler( Scheduled ):
	priority = float( '-inf' )   # try to get into last place in the _RunPending() queue
	def __init__( self, world ):
		self.parent = world      # this automatically sets self.world which in turn automatically schedules the first update
	def _Update( self ):
		world = self.world       # this automatically de-references the underlying weakref
		stimuli = world.stimuli
		keys = world._accel.GetUpdatedKeys()
		processEach = self.Process
		for key in keys.split():
			if key.startswith( '/stimuli' ):
				_, _, stimulusName, propertyName = key.split( '/' )
				stimulus = stimuli.get( stimulusName, None )
				if stimulus is None:
					if propertyName == 'visible': value = 0    # stimuli that have "left" the stage are automatically considered invisible for chronicling purposes
					else: print( 'cannot get %s from a stimulus that has left the stage' % propertyName ); continue
				else: value = getattr( stimulus, propertyName )
				processEach( key, value )
		self.ProcessBatch()
	def Process( self, key, value ):
		print( '%s %s' % ( key, value ) ) # overshadow this in your subclass
	def ProcessBatch( self ):
		pass # overshadow this in your subclass

	
#class Bunch( dict ):
#	def __init__( self, *pargs, **kwargs ): dict.__init__( self ); self.__dict__ = self.update( *pargs, **kwargs )
#	def update( self, *pargs, **kwargs ): [ dict.update( self, d ) for d in pargs + ( kwargs, ) ]; return self
	
class Bunch( dict ):
	def __getattr__( self, name ): return self[ name ] if name in self else getattr( {}, name )
	def __setattr__( self, name, value ): self[ name ] = value
	def __dir__( self ): return self.keys()
	def update( self, *pargs, **kwargs ): [ dict.update( self, d ) for d in pargs + ( kwargs, ) ]; return self
	_getAttributeNames = __dir__
		
def LoadImage( filename, convert=False ):
	"""
	`filename` must be a single filename (not a glob pattern)
	although (experimentally) it may also be a URL. A list of
	PIL `Image` objects (one per frame) is returned.
	
	If `convert` is `True`, convert each PIL object to a `numpy`
	array before returning the list.
	"""
	if not Image: raise ImportError( 'cannot load textures from file unless you install the `PIL` or `pillow` package' )
	url = None
	if filename.startswith( ( 'http://', 'https://' ) ):
		try: import urllib.request
		except ImportError: from urllib import urlretrieve
		else:
			from urllib.request import urlretrieve
			opener = urllib.request.build_opener()
			opener.addheaders = [ ( 'User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36' ) ]
			urllib.request.install_opener( opener )
		url = filename
		xtn = os.path.splitext( url )[ -1 ]
		import tempfile; f = tempfile.NamedTemporaryFile( suffix=xtn, delete=False ); filename = f.name; f.close()
		urlretrieve( url, filename )
	img = Image.open( filename )
	nFrames = getattr( img, 'n_frames', 1 )
	if nFrames == 1:
		frames = [ img ] # most images will be like this
	else:
		# ...but now we're on to multi-frame images. pillow will support these, old PIL will not.
		# Also, we have to work around a bug in pillow whereby the palette is lost on the second
		# and subsequent frames you read. One workaround is to read the palette at the beginning
		# and then put it back into the image repeatedly on each subsequent frame.  That doesn't
		# take account of the possibility that the palette might change from frame to frame. The
		# following does do so. Remove either of the #necessary lines, and palettes will be lost
		frames = [ None ] * nFrames
		canvas = frames[ 0 ] = Image.new( 'RGBA', img.size )
		dispose = None
		for i in range( nFrames ):
			if i:
				canvas = frames[ i ] = frames[ i - 1 ].copy() # sequential composition (in some GIFs, some frames will be just difference frames)
				if dispose: canvas.paste( *dispose )
				img.close(); img = Image.open( filename ) #necessary
				img.n_frames  #necessary (magic...)
				img.seek( i )
			try: canvas.alpha_composite
			except: canvas.paste( Image.alpha_composite( canvas.crop( img.dispose_extent ), img.convert( 'RGBA' ).crop( img.dispose_extent ) ), img.dispose_extent )
			else: canvas.alpha_composite( img.convert( 'RGBA' ), img.dispose_extent[ :2 ], img.dispose_extent )
			dispose = [ (0,0,0,0), img.dispose_extent ] if img.dispose else None
		img.close()
	try: url and os.remove( filename )
	except: Announce( 'failed to delete %s' % filename )
	if convert: frames = [ numpy.array( frame ) for frame in frames ]
	return frames

def AsImageFrames( source ):
	"""
	An image frame may be specified by a filename or URL that indicates
	an image file, or it may be a numpy array (height-by-width, or
	height-by- width-by-channels) of pixel values (either floating-point
	values in the range 0 to 1, or 8-bit unsigned integers).

	The `source` argument to this function may denote a single frame, or
	multiple frames. Multiple frames can be given as a tuple or list of
	frame specifications, or as a glob pattern (including `?` and `*`
	characters) that matches multiple image files, or as a single
	filename/URL that denotes a multi-frame image such as an animated GIF.
	
	If you are passing just a single frame, then it can also be a
	list-of-lists(-of-lists) of pixel values, suitable for immediate
	conversion to a 2- or 3-dimensional numpy array.
	
	Whichever way you specify multiple frames, this function loads the
	frames into memory and returns them as a list of 3-dimensional
	numpy arrays.	
	"""
	if isinstance( source, ( tuple, list ) ) and source and not isinstance( source[ 0 ], ( bool, int, float, tuple, list ) ):
		sourceList = source
	else:
		sourceList = [ source ]
	def getfiles( pattern ):
		if pattern.lower().startswith( ( 'http://', 'https://' ) ): return [ pattern ]
		result = sorted( glob.glob( pattern ) )
		if not result: raise FileNotFoundError( 'found no files matching %r' % pattern )
		return result
	sourceList = [ source for element in sourceList for source in ( getfiles( element ) if isinstance( element, basestring ) else [ element ] ) ]
	if not sourceList: raise ValueError( "empty source texture" )
	sourceList = [ source for source in sourceList if source is not None ]
	class framelist( list ): pass
	for sourceIndex, source in enumerate( sourceList ):
		if isinstance( source, basestring ):
			if not Image: raise ImportError( 'cannot load textures from file unless you install the `PIL` or `pillow` package' )
			filename = source
			source = framelist( LoadImage( filename, convert=True ) )
			bad = [ frame for frame in source if frame.dtype == 'object' ]
			if bad: raise ValueError( """\
Oh dear, it looks like the `PIL` (or `pillow`) package failed to decode image pixel
values from %s
This happens with some versions of PIL/pillow and some image formats; the first you
know about it is that you try to convert an `Image` object to a `numpy.array`, and
you see this kind of thing:

	%r
	
(note the `dtype='object'` instead of a numeric type, and the lack of numeric pixel
values).  I don't know why it happens but it's been happening sporadically for years
and I have never been able to find a workaround at the level of the Python code.
Your best bet is probably to try upgrading your installation of `pillow`:

	python -m pip install --upgrade pillow
	
A last resort might be to try converting this particular image to, and saving it in,
a different image format.
""" % ( filename, bad[ 0 ] ) )
		sourceList[ sourceIndex ] = source
	# flatten the list in case it got expanded by multi-frame images:
	sourceList = [ source for item in sourceList for source in ( item if isinstance( item, framelist ) else [ item ] ) ]
	for sourceIndex, source in enumerate( sourceList ):
		if not numpy: raise ImportError( 'cannot manipulate textures unless you install the `numpy` package' )
		if not isinstance( source, numpy.ndarray ):
			source = numpy.array( source )
		while source.ndim < 3:
			source = numpy.expand_dims( source, -1 )
		sourceList[ sourceIndex ] = source
	return sourceList

# TODO:
# 
# - test on ATI, ...
# - test on Windows 8, 7, XP...
# - binary portability and/or performance testing on Ubuntu?
# 
# - Shady.Video:
#   - timing synchronization test on VideoSource updates?
# 
# - simple way of bestowing dynamic properties on foreign stimuli?
# 
# Pyglet-specific bugs:
# - pyglet worlds die on close, when multi-threading
# - PygletWindowing.Window( fullScreenMode=True ):  does not automatically change screen resolution *back* when Window closes
# - On Python 3.0 (but not 2.0, even though both have pyglet 1.2.4)
#   -- the 'space' key is reported by the Event system as 'windows'....(?!)
#   -- the Surface Pro 'return' key is 'return' on one version and 'enter' on the other (both have same code in pyglet.window.key - may be due to arbitary ordering)
# 
# Pygame-specific bugs:
# - with pygame backend + PyEngine, if GL uses pyglet, first World() fails.  Subsequent Worlds seem fine...

# known issues
# ------------
# GLSL 1.2  and hence bad random-noise on macs
# driver-dependent support for .smoothing in DOTS drawMode, lack of .penThickness support when running with --legacy=False, etc
# on mac, with retina displays:
#   using the accelerator, the window size/position you ask for is not what you get (what you get is good, in that the high-res size is returned, but it's just impossible to know what size to ask for)
#   under pyglet, the window size/position you ask for is what you get (but what you get is low-res)
# on mac, everything must be in main thread (otherwise glfw backend dies, pyglet backend does not deliver events)
# 	(this also means we're limited to one World at a time)
# on mac, pyglet back-end does not grok retina displays
# on mac, SetSwapInterval(x) has no effect when x>1
# pygame cannot select screens
# pygame cannot seem to avoid tearing
# foreign stimuli cannot be depth-sorted behind Shady stimuli (but the OpenGL depth test will work, if enabled with `w.Culling(True)` )

# others in same space
# --------------------
# Python:
# 	pyglet
# 	pyshaders (pyglet extension)
# 	PsychoPy (pyglet-based) - does this in fact do shader tricks over and above pyglet?
# 	VisionEgg (pygame-based)
# 	pyEPL
# Matlab:
# 	PsychToolbox
# 	MGL http://www.indiana.edu/~peso/wordpress/software-life/mgl/
