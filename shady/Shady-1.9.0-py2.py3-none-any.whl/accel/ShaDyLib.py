#!/usr/bin/env python
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
This is a Python interface to the ShaDyLib system. It wraps functions loaded from the
libShady dynamic library via ctypes.  The dynamic library must be in the same directory
as this Python file.  Function prototypes are parsed automatically at import time from
ShaDyLib.h, so ShaDyLib.h must also be in the same directory.

Most of the C functions are reinterpreted as object methods:  this module defines
classes ``Window``, ``Renderer``, ``Stimulus``, ``RGBTable`` and ``Property``, to wrap
them.  It also defines various global functions, and the decorators ``MessageCallback``,
``UpdateCallback`` and ``EventCallback``.  Examples of how to use the decorators, and a
minimal test function ``PyTest()``, are provided at the bottom of this file.

Normal usage would be to import this file and use the classes and functions the module
provides. As a quick test, the ``PyTest()`` function can be run by executing this file
directly.

The Python source file also contains copyright and disclaimer information.
"""

__all__ = [
	'ShaDyLibException', 'MessageCallback', 'UpdateCallback', 'EventCallback',
	#'IfStringThenRawString', 'IfStringThenNormalString',
] # global ShaDyLib_* functions from the dylib will be appended to this

import os, sys, ctypes, inspect

try: __file__
except NameError:
	try: frame = inspect.currentframe(); __file__ = os.path.realpath( inspect.getfile( frame ) )
	finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
WHEREAMI = os.path.dirname( __file__ ) 

class Renderer( object ):
	def __init__( self, shaderProgram=None, legacy=True, ptr=None ):
		self._ptr = ptr
		self.__needs_cleanup = False
		if ptr is None and shaderProgram is not None:
			self._ptr = dll.ShaDyLib_Renderer_New( shaderProgram, legacy )
			err = dll.ShaDyLib_ClearError()
			if err: raise( ShaDyLibException( IfStringThenNormalString( err ) ) )
			self.__needs_cleanup = True
	def __del__( self ):
		if self.__needs_cleanup and self._ptr:
			try: dll.ShaDyLib_Renderer_Delete( self._ptr )
			except: pass
			else: self.__needs_cleanup = False
	@property
	def versions( self ): # remember you can only call this from the thread that created the OpenGL context
		return dict( ShaDyLib=( GetVersion(), GetRevision() ), OpenGL=GetOpenGLVersion(), GLSL=GetGLSLVersion() )

				
class Window( object ):
	def __init__( self, width=None, height=None, left=0, top=0, screen=None, frame=False, fullScreenMode=False, visible=True, openglContextVersion=0, legacy=True, glslDirectory="", substitutions="", ptr=None ):
		if width is None: width = height
		if height is None:
			try: width, height = width
			except: height = width
		if height is None: width = height = -1 # full-screen
		self._ptr = ptr
		self.__needs_cleanup = False
		if ptr is None:
			if not screen: screen = 0
			if fullScreenMode in [ None, 'auto' ]: fullScreenMode = width <= 0 and height <= 0 and sys.platform.lower() == 'darwin'
			self._ptr = dll.ShaDyLib_Window_New( width, height, left, top, int( screen ), frame, fullScreenMode, visible, openglContextVersion, legacy, IfStringThenRawString( glslDirectory ), IfStringThenRawString( substitutions ) )
			err = dll.ShaDyLib_ClearError()
			if err: raise( ShaDyLibException( IfStringThenNormalString( err ) ) )
			self.__needs_cleanup = True
	def __del__( self ):
		if self.__needs_cleanup and self._ptr:
			try: dll.ShaDyLib_Window_Delete( self._ptr )
			except: pass
			else: self.__needs_cleanup = False
	accelerated = True
	width  = property( fget = lambda self: self.GetWidth()  )
	height = property( fget = lambda self: self.GetHeight() )
	size   = property( fget = lambda self: ( self.GetWidth(), self.GetHeight() ) )
	
class Stimulus( object ):
	def __init__( self, ptr ): self._ptr = ptr

class RGBTable( object ):
	def __init__( self, ptr ): self._ptr = ptr

class Property( object ):
	def __init__( self, ptr ): self._ptr = ptr
	@property
	def A( self ):
		memoryAddress = self.GetDataPointer()
		numberOfElements = self.GetNumberOfElements()
		typeStr = self.GetDataType()
		self.__array_interface__ = dict( version=3, data=( memoryAddress, False ), shape=( numberOfElements, ), typestr=typeStr )
		try: import numpy
		except ImportError: pass
		else: return numpy.array( self, copy=False )
		import ctypes
		if   typeStr == 'float64': elementType = ctypes.c_double
		elif typeStr == 'float32': elementType = ctypes.c_float
		else: elementType = getattr( ctypes, 'c_' + typeStr )
		return ctypes.cast( memoryAddress, ctypes.POINTER( elementType * numberOfElements ) )[ 0 ]

class PropertyArray( object ):
	def __init__( self, ptr ):
		self._ptr = ptr
		self.A = self.view()
	def __del__( self ):
		#print( 'deleting' ) # TODO - never reached
		if self._ptr:
			try: dll.ShaDyLib_PropertyArray_Delete( self._ptr )
			except: pass
	def view( self ):
		memoryAddress = self.GetDataPointer()
		numberOfStimuli = self.GetNumberOfStimuli()
		numberOfColumns = self.GetNumberOfColumns()
		typeStr = self.GetDataType()
		self.__array_interface__ = dict( version=3, data=( memoryAddress, False ), shape=( numberOfStimuli, numberOfColumns ), typestr=typeStr )
		try: import numpy
		except ImportError: pass
		else: return numpy.array( self, copy=False )
		import ctypes
		if   typeStr == 'float64': elementType = ctypes.c_double
		elif typeStr == 'float32': elementType = ctypes.c_float
		else: elementType = getattr( ctypes, 'c_' + typeStr )
		return ctypes.cast( memoryAddress, ctypes.POINTER( elementType * numberOfColumns * numberOfStimuli ) )[ 0 ]

class ShaDyLibException( Exception ): pass

MessageCallback = ctypes.CFUNCTYPE( ctypes.c_int,    ctypes.c_char_p, ctypes.c_int )
UpdateCallback  = ctypes.CFUNCTYPE( ctypes.c_int,    ctypes.c_double, ctypes.c_void_p )
EventCallback   = ctypes.CFUNCTYPE( None,            ctypes.c_char_p )

@MessageCallback
def NullMessageCallback( msg, lvl=0 ): return 1

__allprototypes__ = []
def LoadSharedLibrary( dllname = None ):
	import platform, re, ctypes.util

	if dllname is None:
		uname = platform.system()
		arch = '64bit' if sys.maxsize > 2 ** 32 else '32bit'
		machine = platform.machine().lower()
		if machine and machine not in [ 'i386', 'x86_64', 'amd64' ]:
			if machine.startswith( 'armv' ): machine = machine.rstrip( 'l' )
			arch = machine
		if   uname.lower().startswith( 'win' ): dllxtn = '.dll'
		elif uname.lower().startswith( 'darwin' ): dllxtn = '.dylib'
		else: dllxtn = '.so'
		PLATFORM = uname + '-' + arch
		dllname = 'libShady-' + PLATFORM + dllxtn
		#print( dllname )
		
	headername = 'ShaDyLib.h'
	
	global dllpath, headerpath
	
	dllpath = ctypes.util.find_library( dllname )  # try the usual places first: current working dir, then $DYLD_LIBRARY_PATH and friends (posix) or %PATH% (Windows)
	if dllpath == None: dllpath = os.path.join( WHEREAMI, dllname ) # if failed, try right next to this .py file
	if not os.path.isfile( dllpath ): dllpath = None
	if dllpath == None: raise ImportError( "failed to find dynamic library " + dllname )
	dllpath = os.path.realpath( dllpath )
	whereisdll = os.path.dirname( dllpath )
	olddir = os.getcwd()
	os.chdir( whereisdll )
	try: dll = ctypes.CDLL( dllpath )
	finally: os.chdir( olddir )
	headerpath = os.path.join( whereisdll, headername )  # expect to find header next to dynamic library, wherever it was
	if not os.path.isfile( headerpath ): headerpath = os.path.join( WHEREAMI, headername )  # failing that, expect to find header next to this Python file
	if not os.path.isfile( headerpath ): raise OSError( "failed to find header %s in directory %s" % ( headername, whereisdll ) )
	
	prototypes = [ line.split( ' , ' ) for line in open( headerpath ).readlines() if line.strip().startswith( 'SHADYLIB_FUNC\x28' ) ]

	ctypetypes = {
		'ShaDyLib_Renderer'   : ctypes.c_void_p,
		'ShaDyLib_Stimulus'   : ctypes.c_void_p,
		'ShaDyLib_RGBTable'   : ctypes.c_void_p,
		'ShaDyLib_Property'   : ctypes.c_void_p,
		'ShaDyLib_PropArray'  : ctypes.c_void_p,
		'ShaDyLib_Window'     : ctypes.c_void_p,
		
		'void *'              : ctypes.c_void_p,
		'const void *'        : ctypes.c_void_p,
		'char *'              : ctypes.c_char_p,
		'const char *'        : ctypes.c_char_p,
		'size_t'              : ctypes.c_size_t,
		'bool_t'              : getattr( ctypes, 'c_bool', ctypes.c_int ),
		'int'                 : ctypes.c_int,
		'unsigned int'        : ctypes.c_uint,
		'double'              : ctypes.c_double,
		'double *'            : ctypes.POINTER( ctypes.c_double ),
		'void'                : None,
		'ShaDyLib_MessageCallback'  : MessageCallback,
		'ShaDyLib_UpdateCallback'   : UpdateCallback,
		'ShaDyLib_EventCallback'    : EventCallback,
	}

	namespace_prefix = 'ShaDyLib_'
	classes          = { 'ShaDyLib_Renderer' : Renderer, 'ShaDyLib_Stimulus' : Stimulus, 'ShaDyLib_RGBTable' : RGBTable, 'ShaDyLib_Property' : Property, 'ShaDyLib_PropArray' : PropertyArray, 'ShaDyLib_Window' : Window }
	semi_hidden      = [  ] # namespace_prefix will be stripped, then the function will be imported as a global function (whether it would normally be treated as a global function or a method) and its name underscored like __this__ to hide it
	hidden           = [  ]   # these will not be wrapped at all

	def wrapfunction( funcptr, outputClass, doc ):
		def function( *args ):
			args = [ IfStringThenRawString( arg ) for arg in args ]
			output = funcptr( *args )
			err = dll.ShaDyLib_ClearError()
			if err: raise( ShaDyLibException( IfStringThenNormalString( err ) ) )
			if outputClass: output = outputClass( ptr=output )
			return IfStringThenNormalString( output )
		function.__doc__ = doc
		return function
	
	def wrapmethod( funcptr, outputClass, doc ):
		def method( self, *args ):
			args = [ IfStringThenRawString( arg ) for arg in args ]
			if not self._ptr: raise ShaDyLibException( 'dynamic library function called with null pointer' )
			output = funcptr( self._ptr, *args )
			err = dll.ShaDyLib_ClearError()
			if err: raise( ShaDyLibException( IfStringThenNormalString( err ) ) )
			if outputClass: output = outputClass( ptr=output )
			return IfStringThenNormalString( output )
		method.__doc__ = doc
		return method

	globalFuncs = {}
	
	def clean( s ): return re.sub( r'\/\*.*\*\/', '', s ).strip()
	
	
	for prototype in prototypes:
		
		restype = clean( prototype[ 0 ].split( ' ', 1 )[ 1 ] )
		funcname = clean( prototype[ 1 ] )
		args = clean( prototype[ 2 ] )
		doc = restype + ' ' + funcname + args + ';'
		__allprototypes__.append( doc )
		args = args.strip( '()' ).split( ',' )
		funcptr = getattr( dll, funcname )
		funcptr.restype = ctypetypes[ restype ]
		outputClass = classes.get( restype, None )
		for prefix, cls in classes.items():
			if funcname.startswith( prefix + '_' ) and funcname not in semi_hidden + hidden:
				methodname = funcname[ len( prefix ) + 1 : ]
				setattr( cls, methodname, wrapmethod( funcptr, outputClass, doc ) )
				break
		else:
			if funcname not in hidden:
				change_name = ( funcname in semi_hidden )
				if funcname.startswith( namespace_prefix ): funcname = funcname[ len( namespace_prefix ) : ]
				if change_name: funcname = '__' + funcname + '__'
				globalFuncs[ funcname ] = wrapfunction( funcptr, outputClass, doc )
				
		args = [ arg.strip().rsplit( ' ', 1 ) for arg in args ]
		if args != [ [ 'void' ] ]:  funcptr.argtypes = tuple( [ ctypetypes[ arg[ 0 ].strip() ] for arg in args ] )	
			
	return dll, globalFuncs

dll, globalFuncs = LoadSharedLibrary()
locals().update( globalFuncs )
__all__ += globalFuncs.keys()
del globalFuncs
del LoadSharedLibrary

if sys.version >= '3': unicode = str;  # bytes is already defined, unicode is not
else: bytes = str # unicode is already defined, bytes is not
def IfStringThenRawString( x ):
	"""
	A string is likely to be either raw bytes already, or utf-8-encoded unicode. A simple
	quoted string literal may or may not be raw bytes, depending on Python version. This
	is a problem.
	
	If x is a string then, regardless of Python version and starting format, return the
	"raw bytes" version of it so that we can send it over a serial port, pass it via
	ctypes to a C function, etc.
	
	If x is not a string, return it unchanged (so you can use this function to filter a
	whole list of arguments agnostically).
	
	See also IfStringThenNormalString()
	"""
	if isinstance( x, unicode ): x = x.encode( 'utf-8' )
	return x
def IfStringThenNormalString( x ):
	"""
	A string is likely to be either raw bytes or utf-8-encoded unicode. Depending on
	Python version, either the raw bytes or the unicode might be treated as a "normal"
	string (i.e. the type you get from an ordinary quoted string literal, and the type
	can be print()ed without adornment). This is a problem.
	
	If x is a string then, regardless of Python version and starting format, return the 
	"normal string" version of it so that we can print it, use it for formatting, make an
	Exception out of it, get on with our lives, etc.
	
	If x is not a string, return it unchanged (so you can feel free to use this function
	to filter a whole list of arguments agnostically).
	
	See also IfStringThenRawString()
	"""
	if str is not bytes and isinstance( x, bytes ): x = x.decode( 'utf-8' )
	return x

del Renderer.New    # only Renderer.__init__() should be calling ShaDyLib_Renderer_New()
del Renderer.Delete # only Renderer.__del__()  should be calling ShaDyLib_Renderer_Delete()
del Window.New      # only Window.__init__() should be calling ShaDyLib_Window_New()
del Window.Delete   # only Window.__del__()  should be calling ShaDyLib_Window_Delete()
del os, sys, ctypes

#########################################################################################
##### Example code ######################################################################
#########################################################################################

import sys

@MessageCallback
def ExampleMessageCallback( msg, lvl=0 ):
	if lvl <= 3:  # ignore messages at debugging levels higher than 3
		print( "ShaDyLib Message (level %d): %s" % ( lvl, IfStringThenNormalString( msg ) ) )
	return 1
	

def PyTest():
	SetErrorCallback( ExampleMessageCallback )
	print( GetVersion() )
	print( GetPlatform() )

if __name__ == '__main__':
	PyTest()
