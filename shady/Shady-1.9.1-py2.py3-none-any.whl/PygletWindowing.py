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
	
import sys
import time

from . import DPI
from . import Timing
from . import DependencyManagement


GenerateEventTimeStamp = Timing.Seconds

def Screens( pyglet_screen_objects=None, pretty_print=False ):
	DPI.SetDPIAwareness() # prevent DPI scaling by Windows
	if pyglet_screen_objects is None:
		pyglet = DependencyManagement.Import( 'pyglet' )
		display = pyglet.canvas.Display()
		pyglet_screen_objects = display.get_screens()
	screens = [ dict(
		number = i + 1,
		name = ( m.get_device_name() if hasattr( m, 'get_device_name' ) else '' ),
		width = m.width,
		height = m.height,
		left = m.x,
		top = m.y,
		hz = m.get_mode().rate
	) for i, m in enumerate( pyglet_screen_objects ) ]
	if not pretty_print: return screens
	for screen in screens: print( '{number}: "{name}" {width:8d} x {height:4d}  @ ({left},{top}) - {hz}Hz'.format( **screen ) )
	
class Window( object ):
	"""
	Contains the pyglet-specific code for providing a window and/or changing the screen mode,
	double-buffering and flipping.  Essentially it provides a blank OpenGL-friendly canvas,
	without itself using any OpenGL code.
	
	To help with re-usability, ``import pyglet`` is confined to methods, because pyglet is
	both thread-sensitive and reliant on extensive global-state tricks.
	"""
	
	versions = {
		'pyglet' : 'thread-sensitive - not yet imported',
	}
	
	@staticmethod
	def TabulaRasa():
		DependencyManagement.Unimport( 'pyglet' )

	@staticmethod
	def CloseAll():
		if 'pyglet' in sys.modules:
			import pyglet
			for w in pyglet.app.windows: w.close()
	
	def __init__( self, width=None, height=None, left=0, top=0, screen=None, frame=False, fullScreenMode=False, visible=True, openglContextVersion=0, legacy=True ):
		
		if openglContextVersion >= 330:
			msg = 'openglContextVersion >= 330 not yet implemented in PygletWindowing back-end'
			if not sys.platform.lower().startswith( 'win' ):
				msg += " (if you didn't explicitly ask for this, maybe try again but explicitly specify legacy=True)"
			raise NotImplementedError( msg )
		DPI.SetDPIAwareness() # prevent DPI scaling by Windows
		
		pyglet = DependencyManagement.Import( 'pyglet' )
		self.versions[ 'pyglet' ] = pyglet.version
		screen_preference = screen
		if screen_preference:
			screens = Screens()
			try: screen = screens[ screen_preference - 1 ]
			except:
				msg = 'Failed to select screen %r. Available screens are:' % screen_preference
				for i, m in enumerate( screens ): msg += '\n   {number}: {name}  {width} x {height} @ ({left},{top}) - {hz} Hz'.format( **m )
				raise ValueError( msg )
		else:
			screen = Screens( [ pyglet.canvas.Display().get_default_screen() ] )[ 0 ]
		
		if width  in [ -1, None ]: width  = screen[ 'width'  ]; left = 0 if screen_preference else screen[ 'left' ]
		if height in [ -1, None ]: height = screen[ 'height' ]; top  = 0 if screen_preference else screen[ 'top'  ]
		if fullScreenMode in [ None, 'auto' ]: fullScreenMode = False
		if fullScreenMode: left, top = screen[ 'left' ], screen[ 'top' ]
		elif screen_preference: left += screen[ 'left' ]; top += screen[ 'top' ]
		
		self.event_handler = self.DefaultEventHandler
		self.excepthook = None
		self.on_close = None
		self.closing = False
		self.__event_t0 = None

		pyglet.window.Window._view_hwnd = 0 # work around pyglet bug, triggered from the session's second window onwards when fullscreen=True or style=WINDOW_STYLE_BORDERLESS (unfixed since 2015 - see https://bitbucket.org/pyglet/pyglet/issues/9/ )
		InitPygletConstants()
		style = pyglet.window.Window.WINDOW_STYLE_DEFAULT if frame else pyglet.window.Window.WINDOW_STYLE_BORDERLESS
		pw = self.__pygletWindow = pyglet.window.Window( width=width, height=height, fullscreen=fullScreenMode, vsync=True, style=style, visible=visible )
		pw.set_location( left, top )
		pw.set_mouse_visible( False )
		pw.on_key_press =     lambda symbol, modifiers: self.HandleEvent( type='key_press', key=symbol, modifiers=modifiers )
		pw.on_key_release =   lambda symbol, modifiers: self.HandleEvent( type='key_release',   key=symbol, modifiers=modifiers )
		pw.on_mouse_press =   lambda x, y, button, modifiers: self.HandleEvent( type='mouse_press', x=x, y=y, button=button, modifiers=modifiers )
		pw.on_mouse_release = lambda x, y, button, modifiers: self.HandleEvent( type='mouse_release',   x=x, y=y, button=button, modifiers=modifiers )
		pw.on_mouse_drag =    lambda x, y, dx, dy, buttons, modifiers: self.HandleEvent( type='mouse_motion',  x=x, y=y, dx=dx, dy=dy, button=buttons, modifiers=modifiers )
		pw.on_mouse_motion =  lambda x, y, dx, dy: self.HandleEvent( type='mouse_motion',  x=x, y=y, dx=dx, dy=dy )
		pw.on_mouse_scroll =  lambda x, y, scroll_x, scroll_y: self.HandleEvent( type='mouse_scroll',  x=x, y=y, dx=scroll_x, dy=scroll_y )
		pw.on_text =          lambda text: self.HandleEvent( type='text', text=text )
		# most of the conventions are pyglet-like rather than pygame-like, except
		# - both mouse_drag and mouse_motion lead to `event.type = 'mouse_motion'` (the difference
		#   is in the content of event.button)
		# - the identity of the pressed/released key is in `event.key` (not `event.symbol`)
		# other potential event handlers:
		#   on_close,  on_resize, on_mouse_enter, on_mouse_leave, on_text_motion, ...
		
	def Clear( self ):
		self.__pygletWindow.clear()
		
	def DefaultDraw( self, dt=None ):
		self.Clear()
		
	def SynchronizeEvents( self, t0ByDrawingClock, currentTimeByDrawingClock ):		
		self.__event_t0 = GenerateEventTimeStamp() - currentTimeByDrawingClock + t0ByDrawingClock

	def HandleEvent( self, **kwargs ):
		if not self.event_handler: return	
		event = Event( t=GenerateEventTimeStamp(), **kwargs )
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
		import pyglet
		if render_func is None: render_func = self.DefaultDraw
		if event_func is None: event_func = self.DefaultEventHandler
		self.event_handler = event_func
		if auto:
			if render_func: pyglet.clock.schedule( render_func )
			pyglet.app.run()
			if render_func: pyglet.clock.unschedule( render_func )
		else:
			pw = self.__pygletWindow
			self.keep_going = True
			while self.keep_going:
				dt = pyglet.clock.tick()
				pw.switch_to()
				pw.dispatch_events()
				pw.dispatch_event( 'on_draw' )
				if not pw.context: break
				if render_func: render_func( dt )
				pw.flip()
		self.event_handler = self.DefaultEventHandler
	
	def Stop( self ):
		self.keep_going = False
		
	def Close( self ):
		self.closing = True
		if getattr( self, 'on_close', None ): self.on_close( 'before' )
		try: self.__pygletWindow.close
		except: pass
		else: self.__pygletWindow.close()
		if getattr( self, 'on_close', None ): self.on_close( 'after' )

	@property
	def width( self ):  return self.__pygletWindow.width
	@property
	def height( self ): return self.__pygletWindow.height
	@property
	def size( self ):   return ( self.__pygletWindow.width, self.__pygletWindow.height )
	@apply
	def visible():
		def fget( self ): return self.__pygletWindow._visible # TODO: no better-supported way?
		def fset( self, value ):
			if callable( value ): value = value()
			self.__pygletWindow.set_visible( value )
		return property( fget=fget, fset=fset )
	
pyglet_constants = {}
pyglet_modifiers = {}
pyglet_buttons   = {}
try: long
except NameError: long = int
def InitPygletConstants():
	global pyglet_constants, pyglet_modifiers, pyglet_buttons
	if pyglet_constants: return
	import pyglet
	for name, value in pyglet.window.key.__dict__.items():
		if not isinstance( value, int ): continue
		pyglet_constants.setdefault( value, [] ).append( name )
		if name.startswith( 'MOD_' ): pyglet_modifiers[ strip_prefix( name, 'MOD_' ).lower() ] = value
	for name, value in pyglet.window.mouse.__dict__.items():
		if not isinstance( value, int ): continue
		pyglet_buttons[ name.lower() ] = value
	pyglet_modifiers = sorted( pyglet_modifiers.items() )
	pyglet_buttons = sorted( pyglet_buttons.items() )
def strip_prefix( name, prefix, replacement='' ):
	return replacement + name[ len( prefix ) : ] if name.startswith( prefix ) else name
def lookup( value, *prefixes ):
	if value is None:
		return None
	elif isinstance( value, ( int, long ) ):
		if 32 < value < 128: return chr( value ) 
		candidates = [ x for x in pyglet_constants.get( value, [] ) ]
		if prefixes: candidates = [ x for x in candidates if x.startswith( prefixes ) ]
		if not candidates: return '???'
		name = candidates[ 0 ]
	else:
		name = value
	name = name.lower()
	name = strip_prefix( name, 'mod_' )
	name = strip_prefix( name, 'motion_' )
	return name	

nice_repr = lambda x: ( '%.3f' % x ) if isinstance( x, float ) else repr( x )
class Event( object ):
	def __init__( self, **kwargs ):
		for field in 'key button modifiers x y dx dy text t'.split(): kwargs.setdefault( field, None )
		self.__dict__.update( kwargs )
		self.key = lookup( self.key )
		if self.modifiers is None: self.modifiers = ''
		else: self.modifiers = ' '.join( k for k, v in pyglet_modifiers if self.modifiers & v )
		if self.button is None: self.button = ''
		else: self.button = ' '.join( k for k, v in pyglet_buttons if self.button & v )
		
		standardize = { 'enter' : 'return', 'space' : ' ' }
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
