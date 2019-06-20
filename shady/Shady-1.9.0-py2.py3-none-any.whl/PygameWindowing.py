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
import time

import pygame
import pygame.locals

from . import DPI
from . import Timing

GenerateEventTimeStamp = Timing.Seconds

def Screens( pretty_print=False ):
	DPI.SetDPIAwareness() # prevent DPI scaling by Windows
	try: from Tkinter import Tk
	except ImportError: from tkinter import Tk
	tkroot = Tk(); tkroot.withdraw()
	primary = dict(
		number = 1,
		name = 'The PygameWindowing back-end has no support for multiple screens',
		width  = tkroot.winfo_screenwidth(),
		height = tkroot.winfo_screenheight(),
		left = 0,
		top = 0,
		hz = 'unknown',
	)
	tkroot.destroy()
	screens = [ primary ]
	if not pretty_print: return screens
	for screen in screens: print( '{number}: "{name}" {width:8d} x {height:4d}  @ ({left},{top}) - {hz}Hz'.format( **screen ) )
	
	
class Window( object ):
	"""
	Contains the pygame-specific code for providing a window and/or changing the screen mode,
	double-buffering and flipping.  Essentially it provides a blank OpenGL-friendly canvas,
	without itself using any OpenGL code.
	"""
	
	versions = {
		'pygame' : pygame.__version__,
	}
	
	needs_help_with_vbl = True
	
	@staticmethod
	def TabulaRasa():
		pass

	@staticmethod
	def CloseAll():
		pygame.display.quit()

	def __init__( self, width=None, height=None, left=0, top=0, screen=None, frame=False, fullScreenMode=False, visible=True, openglContextVersion=0, legacy=True ):
		if openglContextVersion >= 330:
			msg = 'openglContextVersion >= 330 not yet implemented in PygameWindowing back-end'
			if not sys.platform.lower().startswith( 'win' ):
				msg += " (if you didn't explicitly ask for this, maybe try again but explicitly specify legacy=True)"
			raise NotImplementedError( msg )
		self.pygame_screen = None
		DPI.SetDPIAwareness() # prevent DPI scaling by Windows
		if screen not in [ 0, 1, None ]:
			raise ValueError( 'the pygame windowing back-end does not support selection of screens: must leave screen=None' )
		screen = 1
		if width in [ -1, None ] or height in [ -1, None ]:
			screen = Screens()[ screen - 1 ]
			if width  in [ -1, None ]: width, left = screen[ 'width' ], screen[ 'left' ]
			if height in [ -1, None ]: height, top = screen[ 'height' ], screen[ 'top' ]
			
		if fullScreenMode in [ None, 'auto' ]: fullScreenMode = False
		if fullScreenMode: left, top = 0, 0
		self.visible = visible
		os.environ[ 'SDL_VIDEO_WINDOW_POS' ] = "%d,%d" % ( left, top )
		flags = pygame.OPENGL | pygame.HWSURFACE | pygame.DOUBLEBUF
		if not frame: flags |= pygame.NOFRAME
		if fullScreenMode: flags |= pygame.FULLSCREEN	
		pygame.init()
		self.pygame_screen = pygame.display.set_mode( ( width, height ), flags )
		self.wm_info = pygame.display.get_wm_info()
		self.clock = pygame.time.Clock()
		self.excepthook = None
		self.on_close = None
		self.closing = False
		self.__event_t0 = None
		pygame.mouse.set_visible( False )
		pygame.event.get() # flush the event queue
		
	def __del__( self ):
		self.Close()
		
	def Close( self ):
		self.closing = True
		if getattr( self, 'on_close', None ): self.on_close( 'before' )
		if getattr( self, 'pygame_screen', None ):
			self.pygame_screen = None
			self.keep_going = False
			pygame.display.quit()
		if getattr( self, 'on_close', None ): self.on_close( 'after' )
	
	def SynchronizeEvents( self, t0ByDrawingClock, currentTimeByDrawingClock ):		
		self.__event_t0 = GenerateEventTimeStamp() - currentTimeByDrawingClock + t0ByDrawingClock

	def HandleEvent( self, pygame_event ):
		if not self.event_handler: return
		t = GenerateEventTimeStamp()
		t = 0 if self.__event_t0 is None or t is None else t - self.__event_t0
		event = Event( pygame_event, window=self, t=t )
		events = [ event ]
		if events[ 0 ].type == 'key_press' and events[ 0 ].text:
			events.append( Event( pygame_event, window=self, t=t + 0.002 ) )
			events[ 0 ].text = ''
			events[ 1 ].type = 'text'
			events[ 1 ].abbrev = events[ 1 ].abbrev.replace( 'kp', 't' )
			# NB: this crudely emulates pyglet wherein you get an on_key_press callback followed by an on_text callback.
			# What it doesn't capture is key auto-repeat, whereby you get multiple text events between 'key_press' and 'key_release'.
			# (You could call pygame.key.set_repeat( delay, interval ):  that would cause multiple KEYDOWN events to be
			# issued so, in combination with the above, you would get multiple *pairs* of 'key_press' and 'text' events,
			# but that is not exactly the same behaviour as the pyglet backend.)
		for event in events:
			if event.type is None: continue
			try: self.event_handler( event )
			except Exception as err:
				if not self.excepthook: raise
				sys.stderr.write( '\nFailed to handle %s\n' % event )
				self.excepthook( *sys.exc_info() )
	
	def Run( self, render_func=None, event_func=None, auto=False ):
		# NB: `auto` is unused - provided for compatibility with PygletWindowing
		self.keep_going = True
		self.event_handler = event_func
		prev, dt = None, 0.0
		while self.keep_going:
			if render_func: render_func( dt )
			try: pygame.display.flip() # TODO: need vsync
			except: self.keep_going = False; break
			t = Timing.Seconds()
			if prev is None: prev = t
			dt, prev = t - prev, t
			for pygame_event in pygame.event.get():
				self.HandleEvent( pygame_event )
			
	def Stop( self ):
		self.keep_going = False
	
	@apply
	def width():
		def fget( self ): return None if self.pygame_screen is None else self.pygame_screen.get_width()
		return property( fget=fget )
	@apply
	def height():
		def fget( self ): return None if self.pygame_screen is None else self.pygame_screen.get_height()
		return property( fget=fget )
	@apply
	def size():
		def fget( self ): return ( None, None ) if self.pygame_screen is None else self.pygame_screen.get_size()
		return property( fget=fget )
	@apply
	def visible():
		def fget( self ): return True
		def fset( self, value ):
			if not value: sys.stderr.write( 'a pygame-based window cannot be made invisible\n' )
		return property( fget=fget, fset=fset )
		
# pygame events are incredibly irritating - they allow no introspection and you have to import constants
# from pygame just to work out what's going on.  Repackage them:
def strip_prefix( name, prefix, replacement='' ):
	return replacement + name[ len( prefix ) : ] if name.startswith( prefix ) else name
def lookup( value, *prefixes ):
	if value is None:
		return None
	elif isinstance( value, int ):
		if 'K_' in prefixes and 32 < value < 128: return chr( value ) 
		candidates = [ x for x in pygame_constants.get( value, [] ) ]
		if prefixes: candidates = [ x for x in candidates if x.startswith( prefixes ) ]
		if not candidates: return '???'
		name = candidates[ 0 ]
	else:
		name = value
	name = name.lower()
	name = strip_prefix( name, 'k_' )
	name = strip_prefix( name, 'kmod_' )
	if not name.startswith( 'kp_' ): name = strip_prefix( name, 'kp', 'kp_' )
	return name	
pygame_constants = {}
pygame_modifiers = {}
pygame_buttons = { 1 : 'left', 2 : 'middle', 3 : 'right', 4 : 'wheel_up', 5 : 'wheel_down' }
for name, value in pygame.locals.__dict__.items():
	if not isinstance( value, int ): continue
	pygame_constants.setdefault( value, [] ).append( name )
	if name.startswith( 'KMOD_' ): pygame_modifiers[ strip_prefix( name, 'KMOD_' ).lower() ] = value
pygame_modifiers = sorted( pygame_modifiers.items() )

nice_repr = lambda x: ( '%.3f' % x ) if isinstance( x, float ) else repr( x )
class Event( object ):
	def __init__( self, pygame_event, window, t ):
		#print( pygame_event )   # this at least allows a human-readable (if not, unfortunately trivially machine-readable) account of the fields that a given event has
		if   pygame_event.type == pygame.locals.QUIT:    self.type = 'close'
		elif pygame_event.type == pygame.locals.KEYDOWN: self.type = 'key_press'
		elif pygame_event.type == pygame.locals.KEYUP:   self.type = 'key_release'
		elif pygame_event.type == pygame.locals.MOUSEBUTTONDOWN: self.type = 'mouse_press'
		elif pygame_event.type == pygame.locals.MOUSEBUTTONUP:   self.type = 'mouse_release'
		elif pygame_event.type == pygame.locals.MOUSEMOTION:     self.type = 'mouse_motion'
		else: self.type = repr( pygame_event ) # self.type = lookup( pygame_event.type, 'JOY', 'KEY', 'MOUSE', 'NOEVENT', 'USER' )
		self.key = lookup( getattr( pygame_event, 'key', None ), 'K_' )
		if hasattr( pygame_event, 'mod' ): self.modifiers = ' '.join( k for k, v in pygame_modifiers if pygame_event.mod & v )
		else: self.modifiers = ''
		if hasattr( pygame_event, 'button' ): self.button = pygame_buttons.get( pygame_event.button, '???' )
		elif hasattr( pygame_event, 'buttons' ): self.button = ' '.join( pygame_buttons.get( i + 1 ) for i, pressed in enumerate( pygame_event.buttons ) if pressed )
		else: self.button = ''
		self.x, self.y = getattr( pygame_event, 'pos', ( None, None ) )
		self.dx, self.dy = getattr( pygame_event, 'rel', ( None, None ) )
		self.text = getattr( pygame_event, 'unicode', '' )
		# The convention used by Shady (and pyglet, and OpenGL) is that positive y means "up".
		# Pygame events do not comply with that convention, so let's fix them:
		if self.dy is not None: self.dy *= -1
		if self.y is not None: self.y = window.height - self.y - 1
		if self.type == 'mouse_press' and self.button == 'wheel_up':   self.type, self.button, self.dx, self.dy = 'mouse_scroll', '', 0, +1
		if self.type == 'mouse_press' and self.button == 'wheel_down': self.type, self.button, self.dx, self.dy = 'mouse_scroll', '', 0, -1
		if self.type == 'mouse_release' and self.button in [ 'wheel_up', 'wheel_down' ]: self.type = None
		
		standardize = { 'enter' : 'return', 'space' : ' ' }
		self.key = standardize.get( self.key, self.key )
		self.text = standardize.get( self.text, self.text )
		self.abbrev = ''.join( word[ 0 ] for word in self.type.replace( '_unknown', '_?' ).split( '_' ) )
		if   self.abbrev in ( 'kp', 'ka', 'kr', ): self.abbrev += '[' + self.key    + ']'
		elif self.abbrev in ( 't', ):              self.abbrev += '[' + self.text   + ']'
		elif self.abbrev in ( 'mp', 'mr', ):       self.abbrev += '[' + self.button + ']'
		self.t = t
	_fieldOrder = { k : i for i, k in enumerate( 'type key text button modifiers x y dx dy t'.split() ) }
	def _sortKey( self, item ): k, v = item; return ( self._fieldOrder.get( k, 100 ), k )
	def __repr__( self ): return 'Event(' + ', '.join( [ '%s=%s' % ( k, nice_repr( v ) ) for k, v in sorted( self.__dict__.items(), key=self._sortKey ) ] ) + ')'
	def __rshift__( self, candidates ): return self.abbrev in candidates
	__eq__ = __rshift__