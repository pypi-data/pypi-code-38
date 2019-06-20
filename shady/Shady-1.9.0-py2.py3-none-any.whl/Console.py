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
	
]

import os
import re
import sys
import ast
import time
import ctypes
import struct
import atexit
import inspect
import textwrap
import tokenize
import threading
import collections
try: from StringIO import StringIO
except:    from io import StringIO

from . import DependencyManagement

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def reraise( cls, instance, tb=None ): raise ( cls() if instance is None else instance ).with_traceback( tb )
try: Exception().with_traceback
except: exec( 'def reraise( cls, instance, tb=None ): raise cls, instance, tb' ) # has to be wrapped in exec because this would be a syntax error in Python 3.0

WINDOWS = sys.platform.lower().startswith( 'win' )

SCRIPT_THREAD = None
SHELL_THREAD = None

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range( 30, 38 )
STARTCOLOR = '\033[%dm'
ENDCOLOR = '\033[0m'

def Interactive():
	if SHELL_THREAD and SHELL_THREAD.isAlive(): return 'threaded'
	if 'IPython' in sys.modules:
		IPython, iPythonShellInstance, ipythonIsRunning = GetIPython()
		if ipythonIsRunning: return 'main'
	return None
	
def ThreadedShell( on_close=None, user_ns='this', threaded=True, prefer_ipython=True ):
	"""
	One nice and highly educational way of debugging, designing or otherwise
	interacting with a `Shady.World` is to do so from an interactive prompt. This is
	easy on Windows - a `Shady.World` can be run in a background thread, so it can
	simply be started from an ongoing IPython session.  In many other OSes, this is
	not possible, because the windowing back-end typically insists on being in the
	main thread, crashing or behaving weirdly if not.
	
	This utility function turns the problem inside-out by starting an interactive
	shell in a background thread. Call this function at the end of your script but
	before `world.Run()`.  Launch your script through the ordinary Python interpreter.
	
	Example::
		
		if not world.threaded:  Shady.ThreadedShell( world.Close ); world.Run()
	
	The third-party package `IPython` is recommended, and is used if installed.
	""" # TODO: doc is shady-specific whereas this module is actually more generically reusable
	IPython, iPythonShellInstance, ipythonIsRunning = GetIPython( not prefer_ipython )
	if ipythonIsRunning: return Announce( 'It looks like IPython is already running - an additional ThreadedShell will not be started.' )
	if user_ns == 'this': user_ns = 0
	if isinstance( user_ns, int ):
		try:
			frame = inspect.currentframe()
			for i in range( abs( user_ns ) + 1 ): frame = frame.f_back
			user_ns = frame.f_locals
		finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	if threaded:
		global SHELL_THREAD
		if SHELL_THREAD and SHELL_THREAD.isAlive(): return Announce( 'It looks like ThreadedShell is already running - an additional ThreadedShell will not be started.' )
		else: SHELL_THREAD = threading.Thread( target=ThreadedShell, kwargs=dict( user_ns=user_ns, threaded=False, on_close=on_close, prefer_ipython=prefer_ipython ) )
		SHELL_THREAD.start()
		return SHELL_THREAD
	#if user_ns is not None: user_ns = dict( user_ns )   # why did we do this? was this ever valuable for some reason?
	if not isinstance( on_close, ( tuple, list ) ): on_close = [ on_close ]
	if prefer_ipython and IPython and hasattr( IPython, 'start_ipython' ):
		IPython.start_ipython( argv=[], user_ns=user_ns ) # this is the payload!
		for func in on_close: func and func()
		# The rest is to work around a thread-related ProgrammingError exception from SQLite that happens at system exit:
		IPython, iPythonShellInstance, ipythonIsRunning = GetIPython()
		RemoveIPythonAtExitHandler( iPythonShellInstance, runNow=True )
		if not hasattr( iPythonShellInstance, 'keep_running' ): iPythonShellInstance.keep_running = False
	else:
		if prefer_ipython:
			if IPython: excuse = 'IPython version possibly too old?'
			else: excuse = str( IPython )
			Announce( '\nThe enhanced interactive shell is not available (%s). Trying fallback shell...\n' % excuse )
		print( sys.version )
		if user_ns is None: user_ns = {}
		while OneInteractiveCommand( user_ns ): pass
		for func in on_close: func and func()

def PrintExceptionInfo():
	sys.excepthook( *sys.exc_info() )
	try: sys.stderr.flush()
	except: pass
	return True

def OneInteractiveCommand( user_ns ):
	# TODO: multi-line (indented) inputs
	try: getcmd = raw_input
	except: getcmd = input
	prompt = dict( start='>>> ', block_continuation='... ', other_continuation='... ' )
	mode = 'start'
	cmd = ''
	while True:
		try: line = getcmd( prompt[ mode ] )
		except SystemExit: return False # signal that the interactive session has been closed
		except EOFError: return mode != 'start'
		except KeyboardInterrupt as exc: print( exc ); return True # do nothing, but don't signal the end of interaction
		if not line:
			if mode == 'start': return 'empty' # TODO
			else: break
		while line.startswith( tuple( prompt.values() ) ): line = line[ 4: ]
		if mode == 'start' and not line.strip(): return True # blank input: do nothing, but don't signal the end of interactivity
		cmd += ( '\n' if cmd else '' ) + line
		try: co = compile( cmd, 'user interactive input', 'single' )
		#except KeyboardInterrupt as exc: print( exc ); return True # TODO: necessary?
		except SyntaxError as exc:
			if str( exc ).lower().startswith( 'unexpected eof' ):
				if line.strip( '\x04' ) or cmd.strip( '\x04' ): mode = 'block_continuation'
				else: return False
			elif str( exc ).lower().startswith( 'eof while' ):
				mode = 'other_continuation'
			elif mode == 'start':
				return PrintExceptionInfo()
		except: return PrintExceptionInfo()
		else:
			if mode != 'block_continuation': break
		if mode == 'start': break
	try: co = compile( cmd, 'user interactive input', 'single' )
	#except KeyboardInterrupt as exc: print( exc ); return True # TODO: necessary?
	except: return PrintExceptionInfo()
	try: exec( co, user_ns, user_ns ) 
	except KeyboardInterrupt as exc: print( exc )
	except SystemExit: return False
	except: return PrintExceptionInfo()
	return True
	
def GetIPython( forget_import=False ):
	was_imported = 'IPython' in sys.modules
	IPython = DependencyManagement.Import( 'IPython', packageName='ipython', registerVersion=True )
	instance = None
	isRunning = False
	if not instance:
		try: instance = IPython.get_ipython()
		except: pass
	if not instance:
		try: instance = get_ipython()
		except: pass
	if not instance:
		try: instance = __IPYTHON__  # you goalpost-moving m**********rs
		except: pass
	isRunning = instance is not None and not getattr( instance, 'exit_now', False ) and getattr( instance, 'keep_running', True )
	if forget_import and was_imported:
		for x in list( sys.modules ):
			if x == 'IPython' or x.startswith( 'IPython.' ): sys.modules.pop( x )
	return IPython, instance, isRunning

def CreateEmbeddedIPython( user_ns, banner1='', confirm_exit=False ):
	IPython = DependencyManagement.Import( 'IPython', packageName='ipython', registerVersion=True )
	if not IPython: return None
	InteractiveShellEmbed = None
	if not InteractiveShellEmbed:
		try: from IPython.terminal.embed import InteractiveShellEmbed
		except ImportError: pass
	if not InteractiveShellEmbed:
		try: from IPython.frontend.terminal.embed import InteractiveShellEmbed
		except ImportError: pass
	try: IPython.Config
	except: return InteractiveShellEmbed( confirm_exit=confirm_exit, banner1=banner1, user_ns=user_ns )
	else:
		config = IPython.Config()
		config.InteractiveShellEmbed.confirm_exit = confirm_exit
		return InteractiveShellEmbed( config=config, banner1=banner1, user_ns=user_ns )	
	

def RemoveIPythonAtExitHandler( iPythonShellInstance, runNow=True ):
	try:
		all_handlers = atexit._exithandlers # only available in Python 2.x
	except:
		ip_handlers = iPythonShellInstance.atexit_operations # unfortunately, this will presumably break sooner or later as IPython evolves (it has a track record of moving goalposts that we rely on in exactly this kind of workaround) 
		atexit.unregister( ip_handlers ) # only available in Python 3.x
	else:
		class fpklist( list ): __call__ = lambda self: [ func( *pargs, **kwargs ) for func, pargs, kwargs in self ]
		ip_handlers = fpklist( item for item in all_handlers if 'IPython' in repr( item ) )
		for item in ip_handlers: all_handlers.remove( item )
	if runNow:
		try: ip_handlers()
		except: pass
	return ip_handlers

def Announce( msg, wrapWidth=79 ):
	msg = str( msg ) + '\n'
	if wrapWidth: 
		stripped = msg.lstrip( '\n' ); before = msg[ :len( msg ) - len( stripped ) ]
		stripped = msg.rstrip( '\n' ); after  = msg[ len( stripped ): ]
		msg = before + '\n'.join( textwrap.wrap( msg, wrapWidth ) ) + after
	sys.stderr.write( msg )
	try: sys.stderr.flush()
	except: pass

class MainLoop( object ):
	__stop = object()
	__slots__ = [ '__sleep', '__queue', '__running', 'check' ]
	def __init__( self, sleep=0.001, check=None ):
		self.__running = False
		self.__queue = collections.deque()
		self.__sleep = 0.001
		self.check = check
	running = property( lambda self: self.__running )
	def Queue( self, func, *pargs, **kwargs ):
		container = []
		if func: self.__queue.append( ( func, pargs, kwargs, container ) )
		return container
	def WaitFor( self, func, *pargs, **kwargs ):
		container = self.Queue( func, *pargs, **kwargs )
		while not container: time.sleep( 0.001 )
		if len( container ) > 1: reraise( *container )
		return container[ 0 ]
	def Run( self ):
		if self.__running: return
		self.__running = True
		while True:
			try:
				try:
					func, pargs, kwargs, container = self.__queue.popleft()
				except IndexError:
					if self.check and not self.check(): break
					time.sleep( self.__sleep )
				else:
					if func is self.__stop: break
					try: container.append( func( *pargs, **kwargs ) )
					except: container.extend( sys.exc_info() )
			except KeyboardInterrupt:
				pass
		self.__running = False
	def Stop( self, cancel_pending=False ):
		if cancel_pending: self.__queue.clear() # not sure if thread-safe - if not, could pop() until empty instead
		if self.__running: self.Queue( self.__stop )

def AsDocString( src ):
	if isinstance( src, ( tuple, list ) ): src = '\n'.join( src )
	src = src.strip()
	try: value = ast.literal_eval( src )
	except: value = None
	if not isinstance( value, basestring ): return None
	
	return value

def GetScriptContent( script ):
	if script == '-':
		content = sys.stdin.read()
	elif isinstance( script, list ):
		content = script
	elif isinstance( script, str ) and ( '\n' in script or '\r' in script or not os.path.isfile( script ) ):
		content = script
	else:
		fh = open( script, 'rt' ) if isinstance( script, str ) else script
		content = fh.read()
	if isinstance( content, str ): content = content.replace( '\r\n', '\n' ).replace( '\r', '\n' )
	content = UnindentCommon( MultilineStrip( content ) )
	return content

def ParseInteractiveScript( script, color=True, rst=False ):
	content = GetScriptContent( script )
	if '"""#:' in '\n'.join( content ) or "'''#:" in content: return ParseInteractiveScript2( content, color=color, rst=rst )
	
	intro = []; intros = [ intro ]
	preview = []; previews = [ preview ]
	cellToken = '# --'
	cellIndex = 0
	code = [ 0, '\n' ]
	mainCheckPattern = re.compile( r'''^if\s+__name__\s*==\s*['"]__main__['"]\s*:(\s*#.*)?$''' )
	for line in content:
		line = line.rstrip()
		stripped = line.lstrip()
		indent = line[ :-len( stripped ) ]
		isComment = stripped.startswith( '#' )
		isCellBegin = ( stripped == cellToken or stripped.startswith( cellToken + ' ' ) )
		isMainCheck = re.match( mainCheckPattern, stripped )
		if isCellBegin:
			cellIndex += 1
			intro = []; intros.append( intro )
			preview = []; previews.append( preview )
			if len( stripped ) > len( cellToken ): intro.append( stripped[ len( cellToken ): ] )
			code += [ indent, cellIndex, '\n' ]
		else:
			code.append( line + '\n' )
			if isComment and cellIndex > 0 and not preview:   # we've had a cell marker on a previous line, and the current line is a comment (but not a cell marker) and we haven't started adding code to the preview yet
				intro.append( stripped[ 1: ] )
			elif not isMainCheck or cellIndex > 0 or ( preview and AsDocString( preview ) is None ):
				if preview or ( stripped and ( not isComment or cellIndex > 0 ) ): preview.append( line )
	
	cells = []
	anyCode = False
	for cellIndex, ( intro, preview ) in enumerate( zip( intros, previews ) ):
		preview = TabsToSpaces( preview, extra_indent='    ' )
		if cellIndex == 0:
			docstring = AsDocString( preview.strip() )
			if docstring is not None:
				intro = docstring.lstrip( '\n' ).rstrip().split( '\n' )
				preview = ''
		intro = TabsToSpaces( UnindentCommon( intro ) )
		if color: intro, preview = ColorizeIntro( intro ), ColorizePreview( preview )
		intros[ cellIndex ] = intro
		previews[ cellIndex ] = preview
		hasCode = len( preview.strip() ) > 0
		if hasCode: anyCode = True
		mode = 'pause for code' if hasCode else 'pause to read'
		cell = ( '\n' if intro or preview else '' ) + intro + ( '\n\n' if intro and preview else '' ) + preview + ( '\n' if intro or preview else '' )
		cell = cell.replace( '\t', '    ' )
		cells.append( ( cell, mode ) )
	
	code = ''.join( ( '_SHADY_CONSOLE_INTERACT( %r, %r )' % cells[ x ] ) if isinstance( x, int ) else x for x in code )
	return code, anyCode

def ParseInteractiveScript2( script, color=True, rst=False ):
	lines = GetScriptContent( script )
	gen = ( line + '\n' for line in lines )
	try: readline = gen.next
	except: readline = gen.__next__
	tokens = list( tokenize.generate_tokens( readline ) )
	if 'TokenInfo' not in tokens[ 0 ].__class__.__name__:
		tokens = [ collections.namedtuple( 'TokenInfo', 'type string start end line' )( *t ) for t in tokens ]

	blocks = []			
	for i in range( len( tokens ) ):		
		if i >= len( tokens ) or tokens[ i ].type not in [ tokenize.STRING ]: continue	
		introToken = tokens[ i ]
		
		i += 1
		if i >= len( tokens ) or tokens[ i ].type not in [ tokenize.COMMENT ] or tokens[ i ].string not in [ '#.', '#:', '#>' ]: continue
		commentToken = tokens[ i ]
		
		i += 1
		if i >= len( tokens ) or tokens[ i ].type not in [ tokenize.NL, tokenize.NEWLINE ]: continue
		blocks.append( dict(
			introString = ast.literal_eval( introToken.string ),
			commentType = commentToken.string,
			commentLine = commentToken.start[ 0 ] - 1,
			commentColumn = commentToken.start[ 1 ],
			endPreviousBlock = introToken.start[ 0 ] - 1,
		) )

	anyCode = False
	for i, block in enumerate( blocks ):
		intro = TabsToSpaces( UnindentCommon( MultilineStrip( block[ 'introString' ] ) ) )
		if color: intro = ColorizeIntro( intro )
		preview = ''
		if block[ 'commentType' ] in [ '#:' ]:
			previewStart = block[ 'commentLine' ] + 1
			previewStop = blocks[ i + 1 ][ 'endPreviousBlock' ] if i + 1 < len( blocks ) else None
			preview = TabsToSpaces( MultilineStrip( lines[ previewStart : previewStop ] ), extra_indent='    ' )
			if color: preview = ColorizePreview( preview ) # if you get IndentationError here, add  ""#> or  ""#.  immediately above the unindented block to separate it from this one
		if intro: intro = '\n' + intro + '\n'
		if preview: preview += '\n'
		display = intro + ( '\n' if intro and preview else '' ) + preview
		if display: anyCode = True
		block[ 'display' ] = display
		if block[ 'commentType' ] in [ '#>' ]: block[ 'mode' ] = 'continue'
		elif preview: block[ 'mode' ] = 'pause for code'
		else: block[ 'mode' ] = 'pause to read'
		
	code = ''
	for i, line in enumerate( lines ):
		if blocks and i == blocks[ 0 ][ 'commentLine' ]:
			block = blocks.pop( 0 )
			column = block[ 'commentColumn' ]
			if block[ 'display' ]: interaction = ( ';_SHADY_CONSOLE_INTERACT(%r,%r)' % ( block[ 'display' ], block[ 'mode' ] ) )
			else: interaction = ''
			code += line[ :column ] + interaction + '\n'
		else:
			code += line + '\n'
	return code, anyCode
	
def ColorizeIntro( intro ):
	if not intro: return intro
	return ( STARTCOLOR % GREEN ) + intro + ENDCOLOR

def ColorizePreview( preview ):
	if not preview: return preview
	startCode    = STARTCOLOR % CYAN
	startComment = STARTCOLOR % YELLOW
	
	#kludgy shortcut but sometimes more robust:
	#return ''.join( startCode + re.sub( '(#.*)', ENDCOLOR + startComment + '\\1', line ) + ENDCOLOR + '\n' for line in preview.split( '\n' ) )
	
	comments = {}
	for ttype, tstr, ( lineNumber, start ), _, _ in tokenize.generate_tokens( StringIO( preview ).readline ):
		if ttype == tokenize.COMMENT: comments[ lineNumber - 1 ] = start
	out = ''
	for i, line in enumerate( preview.split( '\n' ) ):
		commentStart = comments.get( i, None )
		if commentStart is None: out += startCode + line + ENDCOLOR + '\n'
		else:                    out += startCode + line[ :commentStart ] + ENDCOLOR + startComment + line[ commentStart: ] + ENDCOLOR + '\n'
	return out
	
def MultilineStrip( lines ):
	if isinstance( lines, str ): lines = lines.split( '\n' )
	else: lines = list( lines )
	if lines and not lines[  0 ].strip(): lines.pop(  0 )
	if lines and not lines[ -1 ].strip(): lines.pop( -1 )
	return lines
		
def UnindentCommon( lines ):
	if isinstance( lines, str ): lines = lines.split( '\n' )
	indicesToNonEmptyLines = [ i for i, line in enumerate( lines ) if len( line.strip() ) ]
	while indicesToNonEmptyLines and lines[ indicesToNonEmptyLines[ 0 ] ]:
		char = lines[ indicesToNonEmptyLines[ 0 ] ][ 0 ]
		if not char.isspace(): break
		if not all( lines[ i ].startswith( char ) for i in indicesToNonEmptyLines ): break
		for i in indicesToNonEmptyLines: lines[ i ] = lines[ i ][ 1: ]
	return lines

def TabsToSpaces( lines, extra_indent='' ):
	if isinstance( lines, str ): lines = lines.split( '\n' )
	return '\n'.join( extra_indent + re.sub( r'^(\t+)', lambda m: ' ' * 4 * len( m.groups()[0]), line ) for line in lines ).rstrip()
	
class AbortInteraction( Exception ): pass

WINDOWS_CONSOLE_RESET = None
def WindowsConsoleColor( code ):
	try: code = int( code )
	except: pass
	handle = ctypes.windll.kernel32.GetStdHandle( -11 ) # STD_OUTPUT_HANDLE = -11 in Windows API
	global WINDOWS_CONSOLE_RESET
	if WINDOWS_CONSOLE_RESET is None:
		# Adapted from https://stackoverflow.com/a/288556/ (apparently based on IPython's winconsole.py, written by Alexander Belchenko)
		csbi = ctypes.create_string_buffer( 22 )
		result = ctypes.windll.kernel32.GetConsoleScreenBufferInfo( handle, csbi )
		if not result: return
		( bufx, bufy, curx, cury, WINDOWS_CONSOLE_RESET, left, top, right, bottom, maxx, maxy ) = struct.unpack( "hhhhHhhhhhh", csbi.raw )
	bright, r, g, b = 8, 4, 2, 1 # Windows API FOREGROUND_INTENSITY,  FOREGROUND_RED, FOREGROUND_GREEN, FOREGROUND_BLUE
	colors = { GREEN : bright|g, YELLOW : bright|r|g, CYAN : bright|g|b, 0 : WINDOWS_CONSOLE_RESET }
	ctypes.windll.kernel32.SetConsoleTextAttribute( handle, colors[ code ] )

def PreviewScript( txt, mode, isIPython=False ):
	pieces = re.split( r'\033\[(?=[0-9;]+m)', txt )
	written = 0; 
	for i, piece in enumerate( pieces ):
		if i: color, piece = piece.split( 'm', 1 )
		else: color = ''
		if color:
			try: sys.stdout.flush()
			except: pass
			if WINDOWS: WindowsConsoleColor( color )
			else: sys.stdout.write( STARTCOLOR % int( color ) )
			try: sys.stdout.flush()
			except: pass
		sys.stdout.write( piece )
		written += len( piece )
	pause = written and 'pause' in mode.lower()
	code = 'code' in mode.lower()
	if pause: sys.stdout.write( '\n(press %s to %s)\n' % ( 'ctrl-D' if isIPython else 'enter', 'run' if code else 'continue' ) )

def _exec( compiled, user_ns ): exec( compiled, user_ns, user_ns )
def RunScript( script, on_close=None, user_ns=None, color=True, threaded=True, interactive=False, prefer_ipython=True ):
	global SCRIPT_THREAD, SHELL_THREAD
	if SCRIPT_THREAD and SCRIPT_THREAD.isAlive(): threaded = False
	if threaded:
		SCRIPT_THREAD = threading.Thread( target=RunScript, kwargs=dict( script=script, on_close=on_close, user_ns=user_ns, color=color, threaded=False, interactive=interactive, prefer_ipython=prefer_ipython ) )
		SCRIPT_THREAD.start()
		if interactive: SHELL_THREAD = SCRIPT_THREAD
		return SCRIPT_THREAD
	if user_ns is None: user_ns = {}
	user_ns[ '__name__' ] = '__main__'
	ipython = None
	if interactive == 'final': user_ns[ '_SKIP' ] = True
	if interactive:
		if prefer_ipython:
			ipython = CreateEmbeddedIPython( user_ns )
			if not ipython: Announce( "\nFailed to create IPython shell - possibly the `ipython` package has not been installed, or possibly it's an unsupported version. Using fallback shell...\n" )
		if ipython:
			ipython.should_raise = False
			class exit_raise( object ):
				def __init__( self, ipython ): self.ipython = ipython
				def __call__( self ): self.ipython.should_raise = True; self.ipython.ask_exit()
				def __repr__( self ): return 'Type quit() or exit() to exit the interactive script'
			user_ns[ 'quit' ] = user_ns[ 'exit' ] = exit_raise( ipython )
		def _SHADY_CONSOLE_INTERACT( preview, mode='pause' ):
			if user_ns.get( '_SKIP', False ): mode='skip'
			else: PreviewScript( preview, mode, ipython )
			replay = user_ns.get( '_SHADY_CONSOLE_REPLAY', None )
			record = user_ns.get( '_SHADY_CONSOLE_RECORD', None )
			if replay:
				replay()
			elif 'pause' in mode.lower():
				if ipython:
					try: ipython()
					except:
						eclass, einstance, _ = sys.exc_info()
						if eclass.__name__ != 'KillEmbedded': print( '%s: %s' % ( eclass.__name__, einstance ) )
					if ipython.should_raise: raise AbortInteraction()
				else:
					own_command = False
					while True:
						result = OneInteractiveCommand( user_ns )
						if not result: raise AbortInteraction()
						if result == 'empty':
							if own_command: 
								PreviewScript( preview, mode, ipython )
								own_command = False
							else: break
						else: own_command = True
			if not user_ns.get( '_SHADY_CONSOLE_INTERACT', None ): user_ns[ '_SKIP' ] = True
			user_ns[ '_SHADY_CONSOLE_INTERACT' ] = _SHADY_CONSOLE_INTERACT
			if record: record()
			
		user_ns[ '_SHADY_CONSOLE_INTERACT' ] = _SHADY_CONSOLE_INTERACT
		code, anyCode = ParseInteractiveScript( script, color=color )
		print( sys.version )
		instruction = 'Press ctrl-D' if ipython else 'Press return (i.e. enter a blank)'
		if anyCode:
			print( '\nRunning interactive script %s\nType exit() or quit() to abort.' % script )
			if interactive != 'final': print( '%s to run each section of code.' % instruction )
		else: print( '\nno commands found in script %s\n' % script )
	else:
		code = '\n'.join( GetScriptContent( script ) )
	compiled = compile( code, script, 'exec' )
	einfo = []
	try: _exec( compiled, user_ns )
	except AbortInteraction: pass
	except: einfo = sys.exc_info()
	else:
		if interactive:
			if ipython:
				print( '(script has finished - press ctrl-D, or type exit() or quit(), to exit embedded shell)' )
				try: ipython()
				except:
					eclass, einstance, _ = sys.exc_info()
					if eclass.__name__ != 'KillEmbedded': print( '%s: %s' % ( eclass.__name__, einstance ) )
			else:
				print( '(script has finished)' )
				while OneInteractiveCommand( user_ns ): pass
	if not isinstance( on_close, ( tuple, list ) ): on_close = [ on_close ]
	for func in on_close: func and func()
	if ipython: RemoveIPythonAtExitHandler( ipython, runNow=True ) # among other effects (such as saving command history) runNow=True causes objects to be removed from the namespace and garbage-collected
	user_ns[ '_SHADY_CONSOLE_EXCEPTION_INFO' ] = einfo # so let's wait until now to put this in
