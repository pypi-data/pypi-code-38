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
import os
import re
import sys
import math
import time
import shlex
import socket
import weakref
import logging
import tempfile
import warnings
import threading
import subprocess

from . import Timing
from . import Location; from .Location import PackagePath
from . import Dependencies; from .Dependencies import numpy

if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ): return x.decode( 'utf-8' ) if str is not bytes and isinstance( x, bytes ) else x
try: from cStringIO import StringIO
except: from io import StringIO

def ComputerName():
	return os.path.splitext( socket.gethostname() )[ 0 ].lower()

def GetRevision():
	hgrev = '@HGREV@'
	if hgrev.startswith( '@' ):
		hgrev = 'unknown revision'
		possibleRepo = PackagePath( '..', '..' )
		repoSubdirectories = [ entry for entry in os.listdir( possibleRepo ) if os.path.isdir( os.path.join( possibleRepo, entry ) ) ]
		if all( x in repoSubdirectories for x in [ '.hg', 'accel-src', 'python' ] ): # then we're probably in the right place
			errorCode, stdout, stderr = Bang( 'hg id -intb -R "%s"' % possibleRepo )
			if not errorCode: hgrev = stdout
	return hgrev
	
class Logger( object ):
	def __init__( self, filename ):
		self.__starttime = time.time()
		if filename == '-': filename = '<stderr>'
		if filename and filename.startswith( '<' ) and filename.endswith( '>' ):
			self.__filepattern = self.__filename = filename
		else:
			self.__filepattern = os.path.realpath( filename ) if filename else None
			self.__filename = self.__filepattern.format( time.strftime( '%Y%m%d-%H%M%S', time.localtime( self.__starttime ) ) ) if self.__filepattern else None
		self.__level = logging.INFO
		self.__format = '# %(asctime)s %(levelname)s: %(message)s'
		self.__logger = self.__formatter = self.__handler = None
		self.__diverted = {}
		self.logSystemInfoOnClose = self.__filename and os.path.splitext( self.__filename )[ 0 ].lower().endswith( '-full' )
		self.Start()
	
	def __del__( self ):
		self.Close()
	
	__nonzero__ = __bool__ = lambda self: self.__logger is not None
		
	filename  = property( lambda self: self.__filename )
	starttime = property( lambda self: self.__starttime )

	def Start( self ):
		if not self.__filename: return
		# return logging.basicConfig( filename=self.__filename, level=self.__level, format=self.__format )
		if self.__logger: return
		loggerName = __name__ + time.strftime( '.log%Y%m%d%H%M%S', time.localtime( self.__starttime ) )
		self.__logger = logging.getLogger( loggerName )
		self.__logger.setLevel( self.__level )
		self.__formatter = logging.Formatter( self.__format )
		if self.__filename.startswith( '<' ) and self.__filename.endswith( '>' ): self.__handler = logging.StreamHandler( getattr( sys, self.__filename.strip( '<>' ) ) )
		else: self.__handler = logging.FileHandler( self.__filename )
		self.__handler.setLevel( self.__level )
		self.__handler.setFormatter( self.__formatter )
		self.__logger.addHandler( self.__handler )
		self.Log( computer=ComputerName(), filename=self.__filename, starttime=self.__starttime )
	
	def Log( self, *pargs, **kwargs ):
		"""
		The following call::
		
			logger.Log( 'hello world!', a=1, b='two' )
			
		will produce a log entry something like::
		
			# 2018-06-30 18:24:31,786 INFO:  hello world!
			a = 1
			b = 'two'
			
		All arguments are optional: either the comment message
		or the keyword args may be omitted.
		"""
		desaturate = kwargs.pop( '_remove_ansi_escapes', False )
		if not self: return None
		msg = ', '.join( str( x ) for x in pargs )
		for k, v in sorted( kwargs.items() ):			
			msg += '\n%s = %s' % ( k, ReadableRepr( v ) )
		if kwargs: msg += '\n'
		if desaturate: msg = re.sub( r'\033\[[0-9;]*m', '', msg )
		# return logging.info( msg )
		self.__logger.info( msg )
	
	__call__ = Log
	
	def Close( self, *threads ):
		if self.logSystemInfoOnClose:
			threads = threads + ( self.LogSystemInfo( threaded=True, verbose=True ), )
		for thread in threads:
			if thread: thread.join()
		if not self.__logger: return
		handlers = self.__logger.handlers[ : ]
		for handler in handlers:
			try: handler.close(); self.__logger.removeHandler( handler )
			except: pass
		self.__formatter = None
		self.__handler = None
		self.__logger = None
		for streamName in list( self.__diverted.keys() ):
			tee = self.__diverted.pop( streamName )
			tee.flush()
			tee.container[ streamName ] = tee.target
	
	@property
	def text( self ):
		if not self.__filename: return ''
		with open( self.__filename, 'rt' ) as fh:
			return fh.read()
		
	def Cat( self ):
		print( self.text )		
	
	def Eval( self ):
		return Read( self.__filename )
	
	def Edit( self ):
		Bang( [ os.environ.get( 'EDITOR', 'edit' ), self.__filename ] )
	
	
	def LogTimings( self, timings ):
		if not self: return
		timings = getattr( timings, 'timings', timings )
		if not isinstance( timings, dict ): return
		filtered = {}
		indices = [ index for index, values in enumerate( zip( *timings.values() ) ) if any( not math.isnan( value ) for value in values ) ]
		for k, v in timings.items():
			if numpy: v = v[ indices ]
			else: v = [ v[ index ] for index in indices ]
			filtered[ k ] = v
		self.Log( timings=filtered )
		
	def LogSystemInfo( self, threaded=True, verbose=False ):
		if not self: return
		if threaded:
			thread = threading.Thread( target=self.LogSystemInfo, kwargs={ 'threaded' : False, 'verbose' : verbose } )
			thread.start()
			return thread
		if verbose: sys.stderr.write( '\n%s Querying system info...\n' % time.strftime( '%Y-%m-%d %H:%M:%S' ) )
		self.Log( system_info=SystemInfo() )
		if verbose: sys.stderr.write( '\n%s Finished querying system info.\n' % time.strftime( '%Y-%m-%d %H:%M:%S' ) )
		
	def Divert( self, streamName='stderr' ):
		container = sys.__dict__
		if streamName in self.__diverted: return
		if self.__filename == '<%s>' % streamName.lower(): return
		original = container.get( streamName )
		ref = weakref.ref( self )
		self.Log( **{ streamName: '' } )
		write = lambda msg: ref() and ref().Log( '\n%s += r"""\n%s\n"""\n' % ( streamName, msg.rstrip() ), _remove_ansi_escapes=True )
		t = self.__diverted[ streamName ] = container[ streamName ] = Tee( original, write )
		t.container = container
		
def ReadableRepr( x ):
	if isinstance( x, dict ): return '{\n' + ''.join( '\t%r : %s,\n' % ( k, ReadableRepr( v ) ) for k, v in x.items() ) + '}'
	if hasattr( x, 'tolist' ): x = x.tolist()
	if isinstance( x, str ):
		x = x.strip( '\n' )
		if   '\n' in x and '"""' not in x: x = 'r"""\n%s\n"""' % x
		elif '\n' in x and "'''" not in x: x = "r'''\n%s\n'''" % x
		elif "'"  in x and '"'   in x: x = repr( x )
		else:
			if "'" in x:  x = '"%s"' % x
			else:         x = "'%s'" % x
			if '\\' in x: x = 'r' + x
		return x
	return repr( x )
	
def Bang( cmd, shell=False ):
	windows = sys.platform.lower().startswith('win')
	# If shell is False, we have to split cmd into a list---otherwise the entirety of the string
	# will be assumed to be the name of the binary. By contrast, if shell is True, we HAVE to pass it
	# as all one string---in a massive violation of the principle of least surprise, subsequent list
	# items would be passed as flags to the shell executable, not to the targeted executable.
	# Note: Windows seems to need shell=True otherwise it doesn't find even basic things like ``dir``
	# On other platforms it might be best to pass shell=False due to security issues, but note that
	# you lose things like ~ and * expansion
	if isinstance( cmd, str ) and not shell:
		if windows: cmd = cmd.replace( '\\', '\\\\' ) # otherwise shlex.split will decode/eat backslashes that might be important as file separators
		cmd = shlex.split( cmd ) # shlex.split copes with quoted substrings that may contain whitespace
	elif isinstance( cmd, ( tuple, list ) ) and shell:
		quote = '"' if windows else "'"
		cmd = ' '.join( ( quote + item + quote if ' ' in item else item ) for item in cmd )
	try: sp = subprocess.Popen( cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	except OSError as err: return err, '', ''
	output, error = [ IfStringThenNormalString( x ).strip() for x in sp.communicate() ]
	return sp.returncode, output, error
	
def SystemInfo():
	uname = sys.platform.lower()
	if uname.startswith( 'win' ):
		fh = tempfile.NamedTemporaryFile( suffix='.txt', delete=False )
		fh.close()
		filename = fh.name
		resultCode, output, error = Bang( [ 'dxdiag', '/whql:off', '/t', filename ] )
		with open( filename, 'rt' ) as fh: output = fh.read()
		os.remove( filename )
	elif uname.startswith( 'darwin' ):
		resultCode, output, error = Bang( 'system_profiler SPHardwareDataType SPDisplaysDataType SPCameraDataType SPPowerDataType SPDiagnosticsDataType SPMemoryDataType SPUniversalAccessDataType' )
	else:
		output = ''
		for command in """
lscpu
lshw -class display
nvidia-smi
nvidia-settings
fglrxinfo
cat /proc/meminfo
sysctl -a
""".strip().splitlines(): # got these from https://www.cyberciti.biz/hardware/collecting-ubuntu-linux-system-information/
			resultCode, out, error = Bang( command )
			output += '$ %s\n%s\n\n' % ( command, out + error )
	return output

def Read( filename ):
	d = {}
	g = globals()
	g[ 'inf' ] = float( 'inf' )
	g[ 'nan' ] = float( 'nan' )
	with open( filename, 'rb' ) as fh:
		content = fh.read().decode( 'utf-8', errors='ignore' ) # look, I really don't care about things like the (R) symbol after 'Intel' in the (differently-encoded) `dxdiag.exe` output, OK?
	exec( content, g, d )
	return d

class Tee( object ):
	def __init__( self, target, write_callback, buffered=True ):
		self.accumulated = StringIO()
		self.buffered = buffered
		self.target = target
		self.write_callback = write_callback
	def flush( self ):
		txt, self.accumulated = self.accumulated.getvalue(), StringIO()
		if self.write_callback and txt: self.write_callback( txt )
		return self.target.flush()
	def write( self, txt ):
		if self.buffered: self.accumulated.write( txt )
		elif self.write_callback: self.write_callback( txt )
		return self.target.write( txt )
	def writelines( self, lines ):
		write = self.write
		for line in lines: write( line )
	def __getattr__( self, name ):
		return getattr( self.target, name )
