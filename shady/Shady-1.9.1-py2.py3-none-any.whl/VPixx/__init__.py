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
This optional sub-module supports devices by VPixx Inc.

The main purpose is to set the mode of a "ViewPixx" display
(or related "DataPixx" device), as follows::

    from Shady.VPixx import ViewPixx
    vp = ViewPixx( world )
    with vp.SetMode( 'M16' ):
        # ...

If you pass your `Shady.World` instance as the`world` constructor
argument, then the `ViewPixx` object will automatically perform
the appropriate `.SetBitCombiningMode()` calls when the hardware
mode is changed.
"""
__all__ = [
	'ViewPixx',
]
import os
import sys
import inspect
import weakref
import platform
import subprocess

try: __file__
except NameError:
	try: frame = inspect.currentframe(); __file__ = os.path.realpath( inspect.getfile( frame ) )
	finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
WHEREAMI = os.path.dirname( __file__ ) 

def dpxmode( mode=None ):
	uname = platform.system()
	arch = '64bit' if sys.maxsize > 2 ** 32 else '32bit'   # TODO: the architecture of the installed driver may be more important than the current system's architecture
	executable = os.path.join( WHEREAMI, 'bin', uname + '-' + arch, 'dpxmode' )
	args = [ executable ]
	if mode:
		args.append( mode )
		if mode.startswith( 'fake-' ):
			args[ -1 ] = args[ -1 ][ 5: ]
			print( 'not running: ' + ' '.join( args ) )
			return None, mode
	sp = subprocess.Popen( args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	out, err = ( x if isinstance( x, str ) else x.decode( 'utf-8' ) for x in sp.communicate() )
	if sp.returncode or err: raise RuntimeError( err.strip() )
	out = out.strip().split()
	return out[ 0 ], out[ -1 ]
	
class ViewPixx( object ):
	"""
	The purpose of this class is to allow you to control the display
	mode of a ViewPixx display or other DataPixx device (VPixx, Inc).
	It communicates with the device over a USB connection (assuming
	the appropriate driver is installed, as per the manufacturer's
	instructions).  An example of use is as follows::
	
	    w = Shady.World()
	    vp = ViewPixx( world=w )
	    with vp.SetMode( 'M16' ):
	        s = w.Sine( pp=0, sigf=0.01, size=400, contrast=0.04, bg=0.1)
	        w.Run()  # or whatever else you want to do
	
	- `mode='C24'` is normal 8-bits-per-channel RGB color mode
	- `mode='C48'` is 16-bits-per-channel RGB color mode using two
	               horizontally-adjacent pixels in VRAM per visible pixel
	- `mode='M16'` is normal 16-bit mono mode (combining the red and green
	               channel of each pixel, without sacrificing resolution).
	
	If you pass your `Shady.World` instance as the constructor argument
	`world`, then the `ViewPixx` object will automatically perform the
	appropriate `.SetBitCombiningMode()` calls when the hardware mode is
	changed.
	"""
	def __init__( self, world=None, mode=None ):
		if isinstance( world, str ): world, mode = mode, world
		self.__world = weakref.ref( world ) if world else None
		self.__previousMode = self.__mode = None
		self.SetMode( mode )
	def __enter__( self ):
		return self
	def __exit__( self, *pargs ):
		self.SetMode( self.__previousMode )
	def QueryMode( self ):
		self.__mode = dpxmode()[ 0 ]
		return self.__mode
	def SetMode( self, mode ):
		if mode is None: return
		if mode == 0: mode = 'C24'
		if mode == 1: mode = 'M16'
		if mode == 2: mode = 'C48'
		if self.__world and self.__world(): self.__world().SetBitCombiningMode( mode )
		before, after = dpxmode( mode )
		if before is None: before = self.__mode
		self.__previousMode, self.__mode = before, after
		return self
	mode = property(
		fget = lambda self: self.__mode,
		fset = lambda self, value: self.SetMode( value ),
	)
