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
	'Window',
	'Screens',
]
try: apply
except NameError: apply = lambda x: x()
	
import os
import sys
import ast
import time

from . import DPI
from . import Timing
from . import Rendering; from .Rendering import PackagePath, LoadAccelerator # TODO - work around the necessity for this mutual dependency - maybe by removing the distinction between 'devel' and 'bundled' ShaDyLibs?

# home-made `six`-esque stuff:
if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x
try: unichr
except NameError: unichr = chr


def Screens( pretty_print=False ):
	ShaDyLib = LoadAccelerator() # TODO: for now, we use the ShaDyLib module instance that the Rendering submodule has currently imported, because the path-wrangling and accleration preferences will have been dealt with there
	olddir = os.getcwd()
	if pretty_print: print( ShaDyLib.Screens( False ) ); returnValue = None
	else: returnValue = ast.literal_eval( ShaDyLib.Screens( True ) )
	os.chdir( olddir ) # because glfwInit can change directory - https://github.com/glfw/glfw/issues/174
	return returnValue
	
class Window( object ):
	"""
	Contains the ShaDyLib-specific code for providing a window and/or changing the screen mode,
	double-buffering and flipping. This is done by providing a thin compatibility wrapper around
	a binary dynamic library. Unlike the other Windowing options, this performs OpenGL initialization
	and automatic setup of a Renderer (all within the DLL).
	"""
	
	accelerated = True
	
	@staticmethod
	def TabulaRasa():
		pass

	@staticmethod
	def CloseAll():
		raise NotImplementedError( "TODO" )

	def __init__( self, width=None, height=None, left=0, top=0, screen=None, frame=False, fullScreenMode='auto', visible=True, openglContextVersion=0, legacy=True, glslDirectory=None, substitutions='' ):
		
		ShaDyLib = LoadAccelerator() # TODO: for now, we use the ShaDyLib module instance that the Rendering submodule has currently imported, because the path-wrangling and accleration preferences will have been dealt with there
		if glslDirectory is None: glslDirectory = PackagePath( 'glsl' )
		if width  is None: width  = -1
		if height is None: height = -1
		# if fullScreenMode in [ None, 'auto' ]: the dll-wrapper will deal with it on the next line:
		self.excepthook = None
		self.event_handler = self.DefaultEventHandler
		self.on_close = None
		self.closing = False
		self._wrapped_event_receiver = ShaDyLib.EventCallback( self.HandleEvent ) # must assign this wrapped object as an attribute here, otherwise the garbage-collector will get it and the callback will cause a segfault when it happens
		self.__event_t0 = None
		olddir = os.getcwd()
		
		if screen is None: screen = 0
		pixelScaling = None
		try:
			adjusted = dict( left=left, top=top, width=width, height=height )
			pixelScaling = DPI.CheckRetinaScaling( screen=screen, raiseException=True, adjust=adjusted )
			#left, top, width, height = [ adjusted[ field ] for field in 'left top width height'.split() ]  # TODO: would like to uncomment this so that you get the resolution you ask for, but then the coordinates would be inconsistent with Shady.Screens() outputs...
		except OSError as err:
			print( 'Failed to check Retina scaling: ' + str( err ) )
		self._accel = ShaDyLib.Window( width=width, height=height, left=left, top=top, screen=screen, frame=frame, fullScreenMode=fullScreenMode, visible=visible, openglContextVersion=openglContextVersion, legacy=legacy, glslDirectory=glslDirectory, substitutions=substitutions )
		# if pixelScaling: self._accel.SetPixelScaling( pixelScaling ) # TODO: would need to set raiseException=False above; but it doesn't work, anyway---GLFW can only handle 2x scaling
		os.chdir( olddir ) # because glfwInit can change directory - https://github.com/glfw/glfw/issues/174
		self._accel.SetEventCallback( self._wrapped_event_receiver )
		if DPI.GetDPIAwareness() == 0: print( 'Failed to disable DPI scaling (check python.exe properties -> Compatibility)' )
				
	def SynchronizeEvents( self, t0ByDrawingClock, currentTimeByDrawingClock ):		
		self.__event_t0 = t0ByDrawingClock # because the drawing clock and the event-time-stamp-generating clock will be the same, inside the accelerator - ignore currentTimeByDrawingClock
		
	def HandleEvent( self, params ):
		if not self.event_handler: return
		NULL = 'NULL';
		event = eval( 'Event( self, ' + IfStringThenNormalString( params ) + ')' )
		event.t = 0 if self.__event_t0 is None or event.t is None else event.t - self.__event_t0
		try: self.event_handler( event )
		except Exception as err:
			if not self.excepthook: raise
			sys.stderr.write( '\nFailed to handle %s\n' % event )
			self.excepthook( *sys.exc_info() )
				
	def DefaultEventHandler( self, event ):
		print( event )
		if event.type == 'keyup' and event.key in [ 'q', 'escape' ]: self.Close()
		
	def Run( self, render_func=None, event_func=None, auto=True ):
		# ``render_func`` is unused, and included for compatibilty with other windowing implementations
		# ``auto`` is unused, and included for compatibilty with other windowing implementations
		if event_func is None: event_func = self.DefaultEventHandler
		self.event_handler = event_func
		self._accel.Run()
		self.event_handler = self.DefaultEventHandler
	
	def GetRenderer( self ): return self._accel.GetRenderer()
	def Close( self ):
		self.closing = True
		if getattr( self, 'on_close', None ): self.on_close( 'before' )
		try: self._accel.Close
		except: pass
		else: self._accel.Close()
		if getattr( self, 'on_close', None ): self.on_close( 'after' )
	@apply
	def visible():
		def fget( self ): return self._accel.visible
		def fset( self, value ): self._accel.visible = value
		return property( fget=fget, fset=fset )
	@property
	def width( self ): return self._accel.width
	@property
	def height( self ): return self._accel.height
	@property
	def size( self ): return self._accel.size


nice_repr = lambda x: ( '%.3f' % x ) if isinstance( x, float ) else repr( x )
class Event( object ):
	def __init__( self, window, **kwargs ):
		for field in 'type key button modifiers x y dx dy text t'.split(): kwargs.setdefault( field, None )
		self.__dict__.update( kwargs )
		if self.modifiers is None: self.modifiers = ''
		if self.button is None: self.button = ''
				
		# make "up" the positive y direction
		if self.dy is not None: self.dy *= -1
		if self.y is not None: self.y = window.height - self.y - 1
			
		# compute dx, dy for mouse_motion if they're not already there
		if self.type == 'mouse_enter': window.prev_mouse_pos = self.x, self.y
		elif self.type == 'mouse_leave': window.prev_mouse_pos = None, None
		elif self.type == 'mouse_motion':
			prevx, prevy = getattr( window, 'prev_mouse_pos', ( None, None ) )
			if prevx is not None and self.dx is None: self.dx = self.x - prevx
			if prevy is not None and self.dy is None: self.dy = self.y - prevy
			window.prev_mouse_pos = self.x, self.y
		
		if isinstance( self.text, int ): self.text = unichr( self.text )
		
		standardize = { 'enter' : 'return', 'space' : ' ', -1 : 'function' }
		self.key = standardize.get( self.key, self.key )
		self.text = standardize.get( self.text, self.text )
		self.abbrev = ''.join( word[ 0 ] for word in self.type.replace( '_unknown', '_?' ).split( '_' ) )
		if   self.abbrev in ( 'kp', 'ka', 'kr', ): self.abbrev += '[' + self.key    + ']'
		elif self.abbrev in ( 't', ):              self.abbrev += '[' + self.text   + ']'
		elif self.abbrev in ( 'mp', 'mr', ):       self.abbrev += '[' + self.button + ']'
		
	_fieldOrder = { k : i for i, k in enumerate( 'type key text button modifiers x y dx dy t'.split() ) }
	def _sortKey( self, item ): k, v = item; return ( self._fieldOrder.get( k, 100 ), k )
	def __repr__( self ): return 'Event(' + ', '.join( [ '%s=%s' % ( k, nice_repr( v ) ) for k, v in sorted( self.__dict__.items(), key=self._sortKey ) ] ) + ')'
	def __rshift__( self, candidates ): return self.abbrev in candidates
	__eq__ = __rshift__