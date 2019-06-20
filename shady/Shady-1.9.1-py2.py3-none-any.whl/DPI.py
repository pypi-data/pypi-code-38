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
	'SetDPIAwareness',
	'GetDPIAwareness',
	'CheckRetinaScaling',
]

import ctypes, sys
import ast, re, subprocess

def GetDPIAwareness():
	if sys.platform.lower().startswith( 'win' ):
		awareness = ctypes.c_int()
		try: func = ctypes.windll.shcore.GetProcessDpiAwareness
		except: return None
		func( 0, ctypes.byref( awareness ) )
		return awareness.value
	
def SetDPIAwareness( target=2, verbose=False ):
	"""
	This function does nothing on non-Windows platforms (returns True,
	meaning "it's all good").
	
	On Windows, this function attempts to use the Windows API (via ctypes)
	to change the current process's "DPI awareness" flag to one of the
	following levels:
	
	0: I am not going to pretend to be DPI-aware: therefore, the operating
	   system will take over, and may scale my graphical output.
	1: I claim to be DPI aware, but will not claim to be committed to
	   continuous monitoring of potential changes in DPI scaling in future.
	   The OS will initially leave me alone (and things will be pixel-for-pixel)
	   but if screen resolution or scaling changes, then the OS may take over
	   again. (NB: this level may be the best we can achieve on Windows 7 or
	   Vista.)
	2: (default) I claim that I will be continuously DPI-aware throughout my 
	   whole lifetime, so the OS will leave me alone.  This is what we want to
	   aim for, for pixel-for-pixel control.
	
	The awareness level can only be successfully changed once per process lifetime,
	and this includes changes that the OS itself may make when it launches the,
	process, in response to an external .exe.manifest file or because of registry
	entries (created when you check "Disable DPI scaling" in the "Compatibility"
	tab of an .exe file's properties dialog).
	
	This function will return True if the awareness level was either successfully
	changed to, or is already at, the desired level.  It will return False if the
	process is not at, and cannot be switched to, the desired level.
	"""
	if not sys.platform.lower().startswith( 'win' ):
		return True
		
	error = None
	success = False
	awareness = ctypes.c_int()

	try:
		ctypes.windll.shcore.GetProcessDpiAwareness( 0, ctypes.byref( awareness ) )
	except:
		sys.stderr.write( 'could not call GetProcessDpiAwareness\n' )
	else:
		if verbose: print( 'before: %d' % awareness.value )

	try:
		error = ctypes.windll.shcore.SetProcessDpiAwareness( target ) # supposedly this is the Windows 8 and 10 way
	except:
		sys.stderr.write( 'could not call SetProcessDpiAwareness\n' )
		if target:
			try:
				success = ctypes.windll.user32.SetProcessDPIAware() # supposedly this is the Windows-7 way: outcome undefined on Windows 8+ although from preliminary try on Windows 10 it looks like it might be equivalent to target=1
			except:
				sys.stderr.write( 'could not call SetProcessDPIAware\n' )
			else:
				if not success: sys.stderr.write( 'SetProcessDPIAware call failed\n' )
	else:
		if verbose: print( 'target: %d' % target )
		success = not error
	try:
		ctypes.windll.shcore.GetProcessDpiAwareness( 0, ctypes.byref( awareness ) )
	except:
		sys.stderr.write( 'could not call GetProcessDpiAwareness\n' )
	else:
		if verbose: print( ' after: %d' % awareness.value )
		success = awareness.value == target
		
	if not success and error: 
		sys.stderr.write( 'SetProcessDpiAwareness error: 0x%08x\n' % ctypes.c_uint32( error ).value )
	return success

def CheckRetinaScaling( screen=0, raiseException=False, adjust=None ):
	"""
	On non-Mac platforms, this function does nothing and returns `None`.
	
	On macOS, the function returns the pixel scaling factor for the
	screen designated by the zero-based integer index `screen`. For a
	non-Retina screen, this scaling factor will be 1.0, whereas for a
	Retina screen, the function performs a check to ensure that the
	resolution scaling in System Preferences -> Displays is set
	appropriately.  If it is not set appropriately, unfortunately there
	is no workaround: then the function will either print an error
	message to stderr, or (if called with `raiseException=True`) it
	will raise an exception.
	
	Currently the accelerated "ShaDyLib" windowing back-end uses version
	3.2.1 of the GLFW library, which is smart enough to cope with the
	difference between Retina and non-Retina screens, but only if the
	resolution scaling in System Preferences is set to enlarge things by
	exactly the factor dictated by the screen's `backingScaleFactor` 
	property (which is a property internal  to the Mac API). So far (as
	of 2018), Retina screens always have a factor of 2 here, and
	non-Retina screens have a factor of 1.
	
	This means that, if your Retina screen has 2560 x 1600 physical pixels
	for example, its scaling must be set to "Looks like 1280 x 800" in
	System Preferences. If this is not the case, we would end up inferring
	the wrong number of physical pixels and unfortunately there does not
	currently appear to be a way of programming around this in the macOS
	API (see https://stackoverflow.com/a/53712467/ ).
	"""
	if not sys.platform.lower().startswith( 'darwin' ):
		return None

	if screen is None: screen = 0
	
	applescript = """
use framework "AppKit"
set screenIdentifier to {screen}
if screenIdentifier is 0
	set selectedScreen to current application's NSScreen's mainScreen
else
	set theScreens to current application's NSScreen's screens()
	try
		set selectedScreen to item screenIdentifier of theScreens
	on error msg
		return "{{'error':'failed to get info for screen " & screenIdentifier & "'}}"
	end try
end if
set frame to selectedScreen's frame() as list -- the "as list" clauses here are
set origin     to ( item 1 of frame ) as list -- necessary for backward compatibility
set dimensions to ( item 2 of frame ) as list -- with OS X El Capitan
return "{{\
'originX':" & item 1 of origin & ", \
'originY':" & item 2 of origin & ", \
'widthLooksLike':"  & item 1 of dimensions & ", \
'heightLooksLike':" & item 2 of dimensions & ", \
'backingScaleFactor':" & selectedScreen's backingScaleFactor() & "\
}}"
	""".format( screen=screen )

	sp = subprocess.Popen( [ 'osascript' ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False )
	out, err = [ x if x is str else x.decode( 'ascii', errors='ignore' ) for x in sp.communicate( applescript.encode( 'utf-8' ) ) ]
	if err or sp.returncode: raise OSError( 'Applescript returned error code ' + str( sp.returncode ) + ( ': ' if err else '' ) + err  )
	screenInfo = ast.literal_eval( out )
	if 'error' in screenInfo: raise ValueError( screenInfo[ 'error' ] )

	sp = subprocess.Popen( [ 'system_profiler', 'SPDisplaysDataType' ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False )
	out, err = [ x.decode( 'utf-8', errors='replace' ) for x in sp.communicate() ]
	if err or sp.returncode: raise OSError( 'system_profiler returned error code ' + str( sp.returncode ) + ( ': ' if err else '' ) + err  )
	pattern = re.compile( r"""
		^\s*
		Resolution:\s*
		(?P<widthReally>\d+)
		\s*x\s*
		(?P<heightReally>\d+)
		\s*(?P<note>.*?)
		\s*$
	""", re.VERBOSE + re.IGNORECASE )
	resolutionLines = [ matched.groupdict() for line in out.split( '\n' ) for matched in [ re.match( pattern, line ) ] if matched ]
	if not screen: screen = 1
	screenInfo[ 'number' ] = screen
	resolutionLine = resolutionLines[ screen - 1 ]
	for k in resolutionLine:
		try: screenInfo[ k ] = float( resolutionLine[ k ] )
		except: screenInfo[ k ] = resolutionLine[ k ]	
	#print( screenInfo )
	screenInfo[ 'widthShouldLookLike'  ] = int( screenInfo[ 'widthReally'  ] / screenInfo[ 'backingScaleFactor' ] )
	screenInfo[ 'heightShouldLookLike' ] = int( screenInfo[ 'heightReally' ] / screenInfo[ 'backingScaleFactor' ] )
	if max( abs( screenInfo[ 'widthLooksLike'  ] - screenInfo[ 'widthShouldLookLike' ] ), abs( screenInfo[ 'heightLooksLike' ] - screenInfo[ 'heightShouldLookLike' ] ) ) > 0.1:
		msg = 'since screen {number} is a Retina screen, to achieve pixel-for-pixel accuracy its resolution scaling must be set to "Looks like {widthShouldLookLike} x {heightShouldLookLike}" in System Preferences -> Displays, whereas currently it is set to "Looks like {widthLooksLike:g} x {heightLooksLike:g}"'.format( **screenInfo )
		if raiseException: raise RuntimeError( msg )
		else: sys.stderr.write( '%s\n' % msg )
	actualScalingFactor = screenInfo[ 'widthReally' ] / screenInfo[ 'widthLooksLike' ]
	if adjust is not None:
		fields = 'left top width height'.split()
		for field in 'width height'.split():
			if adjust[ field ] > 0: adjust[ field ] /= actualScalingFactor
		if ( screenInfo[ 'originX' ], screenInfo[ 'originY' ] ) == ( 0.0, 0.0 ):
			for field in 'left top'.split(): adjust[ field ] /= actualScalingFactor  # NB: this is a nasty hack favouring the most common use-case at the expense of consistency
	return actualScalingFactor
	
if __name__ == '__main__':
	import sys
	args = getattr( sys, 'argv', [] )[ 1: ]
	target = 2
	if args: target = int( args.pop( 0 ) )
	SetDPIAwareness( target, verbose=True )

