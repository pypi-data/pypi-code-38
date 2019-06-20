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
This module contains various optional (but useful) utility functions.

Note that everything exported from this module is also available in
the top-level `Shady.*` namespace.
"""

__all__ = [
	'Tukey',
	'Hann', 
	
	'EllipticalTukeyWindow',
	'LinearizationTestPattern',
	'CheckPattern',
	
	'RelativeLocation',
	
	'FindGamma',
	'PixelRuler',
	'Cross',
	'Loupe',
	'TearingTest',
	'FrameIntervalGauge',
	'EstimateFrameRate',
	
	'PlotTimings',
	'Histogram',
	
	'VDP', 'PixelsToDegrees', 'DegreesToPixels',

	'CommandLine',
	'WorldConstructorCommandLine', 'AutoFinish',
	'RunShadyScript',
	
	'ComplexPolygonBase', 'Real2DToComplex', 'ComplexToReal2D',
	
	'VideoRecording',
]
import os
import sys
import time
import math
import weakref
import inspect
import warnings
import threading

def reraise( cls, instance, tb=None ): raise ( cls() if instance is None else instance ).with_traceback( tb )
try: Exception().with_traceback
except: exec( 'def reraise( cls, instance, tb=None ): raise cls, instance, tb' ) # has to be wrapped in exec because this would be a syntax error in Python 3.0

from . import Logging
from . import CommandLineParsing; from .CommandLineParsing import CommandLine, CommandLineError
from . import DependencyManagement
from . import Dependencies; from .Dependencies import numpy
from . import Console; from .Console import GetIPython, ThreadedShell, Interactive, MainLoop
from . import Linearization; from .Linearization import Linearize, ApplyLUT

# 1-D helper functions
def Tukey( x, rise=0.5, plateau=0.0, fall='rise', start=0.0 ):
	"""
	This is a one-dimensional windowing function consisting of a raised-
	cosine rise from zero, an optional plateau, and a raised-cosine fall
	back to zero.  It is a generalization of the Hann function. It
	requires the `numpy` package to be installed.
	
	Args:
		x:
			The input argument to the function, in units of space or
			time (let's assume it's time from here on).
		rise:
			In the same units as `x`, the amount of time the function
			takes to rise from 0.0 to 1.0.
		plateau:
			In the same units as `x`, the amount of time for which
			the function remains at 1.0 between the rising and falling
			phases. The default is 0, which means this function returns
			a simple Hann or raised-cosine function by default.
		fall:
			In the same units as `x`, the amount of time the function
			takes to fall from 1.0 back to 0.0.  Alternatively, the
			string `'rise'` may be used (and it is the default) which
			makes the duration of the fall match the duration of the
			rise.
		start:
			In the same units as `x`, the initial amount of time for
			which the function remains at 0.0 before starting to rise.
			Defaults to 0.
		
		
	Returns:
		The numeric output of the window function (as a `float` if the
		input `x` was a scalar numeric; as a `numpy.array` if `x` was
		a sequence or array of numbers).
	"""
	if isinstance( x, ( float, int ) ): cls = float
	else: cls = None
	wasarray = isinstance( x, numpy.ndarray )
	if not wasarray: x = numpy.array( x, dtype=float )
	if fall == 'rise': fall = rise
	start_fall = rise + plateau
	y = numpy.zeros_like( x )
	if start: x = x - start
	x = x.flat
	if rise:
		mask = ( x > 0.0 ) & ( x <= rise )
		scaled = x[ mask ] * ( numpy.pi / rise )
		y.flat[ mask ] = 0.5 - 0.5 * numpy.cos( scaled )
	if plateau:
		mask = ( x > rise ) & ( x <= start_fall )
		y.flat[ mask ] = 1.0
	if fall:
		mask = ( x > start_fall ) & ( x <= start_fall + fall )
		scaled = ( x[ mask ] - start_fall ) * ( numpy.pi / fall )
		y.flat[ mask ] = 0.5 + 0.5 * numpy.cos( scaled )
	if cls: y = cls( y )
	return y

def Hann( x, rise=0.5, start=0.0 ):
	"""
	A Hann window (raised cosine) function of `x`. Wraps around
	the more general `Tukey()` function but ensures no plateau,
	and equal lengths of rise and fall.
	"""
	return Tukey( x, rise=rise, start=start )
	
# image/pattern generation
def AsSize( x, allow_x_to_be_template_array=False ):
	try: x.size[ 1 ]
	except: pass
	else: return x.size[ :2 ]
	if isinstance( x, ( int, float ) ): return [ x, x ]
	try: x.size, x.flat, x.shape
	except: pass
	else:
		if x.size in [ 2, 3 ]: return list( x.flat[ :2 ] )
		elif allow_x_to_be_template_array and len( x.shape ) in [ 2, 3 ]: return list( x.shape[ :2 ] )
	try:
		if len( x ) in [ 2, 3 ]: return [ int( x[ 0 ] ), int( x[ 1 ] ) ]
	except:
		pass
	raise TypeError( 'could not interpret %r as a size specification' % x )
	
def EllipticalTukeyWindow( size, plateauProportion=0.0 ):
	"""
	This function constructs a two-dimensional `numpy.array` of the specified
	`size` containing a discretely sampled one- or two-dimensional spatial
	windowing function. The function has an optional plateau in the center,
	outside of which it falls off to 0 according to a raised cosine profile.
	For two-dimensional windows, all contours of the array are elliptical and
	have the same aspect ratio as the specified `size`.
	
	This function replicates the formula that is used for windowing on the GPU,
	as per the fragment shader program at the heart of Shady.
	
	Args:
		size:
			May be an integer (dictating a square output), a sequence of two
			integers [width, height], a `World` or `Stimulus` instance, or an
			existing 2- or 3-D `numpy.array` to use as a template (i.e. one
			whose first two dimensions are [height, width] ).
		plateauProportion:
			This is either a single floating-point number, or a sequence of two
			numbers corresponding to the horizontal and vertical dimensions.
			The numbers specify the linear proportion of the cross section of
			the window function that is at maximum.  They can be in the range
			0.0 (no plateau => radial Hann window) to 1.0 (all plateau, no
			skirt => sharp-edged circle or ellipse).  Alternatively, negative
			values can be used to disable windowing (so, for example,
			`[0.0, -1.0]`  specifies Hann windowing in the horizontal dimension
			only, and no windowing in the vertical).
		
	Returns:
	    A two-dimensional `numpy.array` containing image pixel multipliers,
	    in the range [0.0, 1.0].
	"""
	width, height = AsSize( size, True )
	
	plateauProportion = numpy.array( plateauProportion, dtype=float ).flatten()
	if plateauProportion.size == 1: plateauProportion = numpy.concatenate( [ plateauProportion ] * 2, axis=0 )
	if plateauProportion.size != 2: raise ValueError( 'plateauProportion must have 1 or 2 elements' )
	ppx, ppy = plateauProportion
	
	vy, vx = numpy.ix_( numpy.arange( height, dtype=float ), numpy.arange( width, dtype=float ) )
	if numpy.isnan( ppx ) or ppx < 0.0 or ppx > 1.0: vx.flat = 0.0; ppx = 1.0
	if numpy.isnan( ppy ) or ppy < 0.0 or ppy > 1.0: vy.flat = 0.0; ppy = 1.0
	vx -= vx.mean(); vx *= 2.0
	vy -= vy.mean(); vy *= 2.0
	v = vx + 1j * vy
	vlen = numpy.abs( v ) 
	vn = v + 0.0
	mask = vlen != 0.0
	vn[ mask ] /= vlen[ mask ]
	ellipseAxes = width * ppx,  height * ppy
	def InverseLength( c, xweight=1.0, yweight=1.0 ):
		if xweight != 1.0 or yweight != 1.0: c = xweight * c.real + 1j * yweight * c.imag
		length = numpy.abs( c )
		length[ length == 0.0 ] = 1.0
		return 1.0 / length
	r_inner = ellipseAxes[ 0 ] * ellipseAxes[ 1 ] * InverseLength( vn, ellipseAxes[ 1 ], ellipseAxes[ 0 ] ) # inner radius, in same units as v along the direction of v
	r_outer = width * height * InverseLength( vn, height, width ) # outer radius, in same units as v along the direction of v
	rlen = vlen - r_inner
	rlen *= InverseLength( numpy.clip( r_outer - r_inner, 0.0, None ) )
	return 0.5 + 0.5 * numpy.cos( numpy.pi * numpy.clip( rlen, 0.0, 1.0 ) )

def LinearizationTestPattern( canvasSize=( 1920, 1080 ), patchSize=( 50, 50 ), amplitudes=( 0.95, 0.75, 0.5, 0.25 ), plateauProportion=0.85, meanZero=True ):
	"""
	Construct a 2-dimensional `numpy.array` containing a special linearization pattern.
	Blank patches are interspersed in checkerboard fashion with textured patches.
	Textured patches contain horizontal stripes, vertical stripes, and checkerboard
	patterns, all of single-pixel granularity. Textured patches vary in contrast.
	When the screen (or stimulus) is perfectly linearized, textured patches of all
	contrasts should be indistinguishable from blank patches when viewed from a
	sufficient distance (or with sufficiently bad uncorrected vision).
	
	Args:
	    canvasSize:
	        may be an `int` (resulting in a square stimulus), or a sequence of
	        two numbers (width, height). May also be a `Shady.World` instance,
	        `Shady.Stimulus` instance, a `PIL` image, or an image represented
	        as a 2- or 3-dimensional `numpy.array` - in these cases the
	        dimensions of the output match the dimensions of the instance.
	    
	    patchSize (sequence of 2 ints):
	        dimensions, in pixels, of the individual patches that make up the
	        pattern in checkerboard fashion.
	    
	    amplitudes (tuple of floats):
	        0.0 means blank, 1.0 means full contrast. 
	    
	    plateauProportion (float):
	        governs the one-dimensional raised-cosine fading at the edges of striped
	        patches.  With `plateauProportion=1`, bright and dark edge artifacts
	        tend to be visible.
	    
	    meanZero (bool):
	        if `True`, then the mean of the output array is 0 and its range is
	        `[-1,1]` when `amplitude=1`.   If `False`, then the mean of the output
	        array is 0.5 and the range is `[0,1]` when `amplitude=1`.
	    
	Returns:
	    A two-dimensional `numpy.array` containing the image pixel values.
	    
	Examples::
	
	    world.Stimulus( LinearizationTestPattern( world ) * 0.5 + 0.5 )
	    world.Stimulus( LinearizationTestPattern( world, meanZero=False ) ) # same as above
	"""
	canvasWidth, canvasHeight = [ int( round( x ) ) for x in AsSize( canvasSize ) ]
	patch = numpy.zeros( patchSize, dtype=float )
	blank = patch
	patches = []
	xfade = EllipticalTukeyWindow( patchSize, [ plateauProportion, None ] )
	yfade = EllipticalTukeyWindow( patchSize, [ None, plateauProportion ] )
	for amplitude in amplitudes:
		lo = -amplitude
		hi = +amplitude
		hstripes = patch + lo
		hstripes[ 0::2, : ] = hi 
		vstripes = patch + lo
		vstripes[ :, 0::2 ] = hi
		if 0.0 <= plateauProportion < 1.0:
			hstripes *= yfade
			vstripes *= xfade
		checks = patch + lo
		checks[ 0::2, 0::2 ] = hi
		checks[ 1::2, 1::2 ] = hi
		patches += [ hstripes, blank, vstripes, blank, checks, blank ]
	height = 0
	while height < canvasHeight:
		row = numpy.concatenate( patches, axis=1 )
		row = numpy.tile( row, ( 1, int( numpy.ceil( float( canvasWidth ) / row.shape[ 1 ] ) ) ) )[ :, :canvasWidth ]
		if height: pattern = numpy.concatenate( [ pattern, row ], axis=0 )
		else: pattern = row
		height += row.shape[ 0 ]
		patches.append( patches.pop( 0 ) )
	pattern = pattern[ :canvasHeight, :, numpy.newaxis ]
	if not meanZero: pattern += 1.0; pattern /= 2.0
	return pattern

def CheckPattern( canvasSize=( 1920, 1080 ), amplitude=1.0, checkSize=1, meanZero=True ):
	"""
	Return a 2-dimensional `numpy.array` containing a checkerboard pattern.
	
	Args:
	    canvasSize:
	        may be an `int` (resulting in a square stimulus), or a sequence of
	        two numbers (width, height). May also be a `Shady.World` instance,
	        `Shady.Stimulus` instance, a `PIL` image, or an image represented
	        as a 2- or 3-dimensional `numpy.array` - in these cases the
	        dimensions of the output match the dimensions of the instance.
	    
	    amplitude (float):
	        0.0 means blank, 1.0 means full contrast. 
	    
	    checkSize (int):
	        size, in pixels, of the individual light and dark squares making up
	        the checkerboard pattern.
	    
	    meanZero (bool):
	        if `True`, then the mean of the output array is 0 and its range is
	        `[-1,1]` when `amplitude=1`.   If `False`, then the mean of the output
	        array is 0.5 and the range is `[0,1]` when `amplitude=1`.
	    
	Returns:
	    A two-dimensional `numpy.array` containing the image pixel values.
	    
	Examples::
	
	    world.Stimulus( CheckPattern( world ) * 0.5 + 0.5 )
	    world.Stimulus( CheckPattern( world, meanZero=False ) )  # same as above
	    
	"""
	canvasWidth, canvasHeight = [ int( round( x ) ) for x in AsSize( canvasSize, True ) ]
	i, j = numpy.ix_( range( canvasHeight ), range( canvasWidth ) )
	i //= checkSize; j //= checkSize
	pattern = ( ( i % 2 ) == ( j % 2 ) ).astype( float )
	if meanZero: pattern *= 2.0; pattern -= 1.0
	return pattern

# custom World behaviours

def AdjustGamma( world, finish=None, target=None, xBlue=True ):
	"""
	This installs the event handler for `FindGamma`.  It does not,
	on its own, create or display a linearization stimulus.
	
	Args:
		world (World):
			The World to which an EventHandler should be added.
			
		finish (callable):
			Function to be called when the user ends the
			gamma-adjustment procedure. Should take one argument:
			the final sequence of three gamma values (if the
			user has indicated acceptance of them) or `None`
			(if not).
		
		target (None, World or Stimulus):
			Object whose `.gamma` setting is to be adjusted.
			By default (with `target=None`) the `target` will
			be the same as the `world`.
		
		xBlue (bool):
			If True, movement on the x axis separately adjusts
			the gamma of the blue channel relative to the others.
			If False, horizontal mouse movement is ignored.
	
	Move the mouse, or tap or drag on the touchscreen, to change
	gamma in real time. Press return to call `finish( gamma )`
	and remove the handler, ending the adjustment procedure.
	Press escape to end the adjustment procedure with a call to
	`finish( None )` instead.  Press any letter key to print the
	current gamma (annotated by the letter that you pressed) to
	the console.
	"""
	slot = -1000
	if target is None: target = world
	
	@world.EventHandler( slot=slot )
	def gamma_adjuster( self, event ):
		adjust = []
		if event.type == 'mouse_motion' and 'left' in event.button:
			delta = 0.02
			if event.dy:
				if event.dy < 0: adjust.append( 'down' )
				if event.dy > 0: adjust.append( 'up' )
			if event.dx:
				if event.dx < 0: adjust.append( 'left' )
				if event.dx > 0: adjust.append( 'right' )
		elif event.type in [ 'key_press', 'key_auto' ] and event.key in [ 'down', 'up', 'left', 'right' ]:
			delta = 0.01
			if 'shift' in event.modifiers: delta *= 10.0
			adjust.append( event.key )
		if adjust:
			if 'ctrl' in event.modifiers or 'control' in event.modifiers: delta /= 10.0
			if 'down' in adjust and min( target.gamma ) > delta: target.gamma -= delta
			if 'up' in adjust: target.gamma += delta
			if 'left' in adjust and xBlue: target.bluegamma -= delta
			if 'right' in adjust and xBlue and target.bluegamma > delta: target.bluegamma += delta
				
		if event.type == 'key_release':
			if event.key in [ 'escape' ]:
				self.SetEventHandler( None, slot=slot ) # removes this event-handler
				if finish: finish( None )
				return True # for the last time, prevents later event-handlers from running
			elif event.key in [ 'enter', 'return' ]:
				self.SetEventHandler( None, slot=slot ) # removes this event-handler
				if finish: finish( target.gamma )
				return True # for the last time, prevents later event-handlers from running
			elif event.key in list( 'abcdefghijklmnopqrstuvwxyz' ):
				print( '\n%s: %s' % ( event.key.upper(), tuple( target.gamma ) ) )
				return True # prevents later event-handlers from running
				            # (hence overrides the q-to-close behavior of the default handler)
	
def FindGamma( world, finish=None, xBlue=True, text=False, **kwargs ):
	"""
	Interactively use a `LinearizationTestPattern` to estimate the correct gamma.
	
	Blank patches are interspersed in checkerboard fashion with textured patches.
	Textured patches contain horizontal stripes, vertical stripes, and checkerboard
	patterns, all of single-pixel granularity. Textured patches vary in contrast.
	When the screen (or stimulus) is perfectly linearized, textured patches of all
	contrasts should be indistinguishable from blank patches when viewed from a
	sufficient distance (or with sufficiently bad uncorrected vision).
	
	The interactive component works best with touch-screens, but you can use the
	mouse. Up-down movement changes the overall gamma. With the option `xBlue=True`,
	left-right movement will also adjust the "color temperature" by varying the
	blue gamma relative to the others (without this, even when the overall gamma
	is neither too high nor too low, the textured patches can look yellower than
	the blank patches on some screens).
	
	Supply an optional callback as `finish`. When you press the return key, the
	adjustment procedure will end and `finish( gamma )` will be called with the
	final empirical gamma values. If you press the escape key instead, the
	adjustment will end by calling `finish( None )` instead.   Press any letter
	key to report the current gamma setting on the console.
	"""
	if 'gammatest' not in world.stimuli:
		world.Stimulus( LinearizationTestPattern( world, **kwargs ) * 0.5 + 0.5, name='gammatest', gamma=world.gamma, anchor=world.anchor )
	if text and 'gamma_readout' not in world.stimuli:
		import Shady.Text
		readout = world.Stimulus( name='gamma_readout', text=lambda t: 'R: %5.3f, G: %5.3f, B: %5.3f' % tuple( world.stimuli.gammatest.gamma ), anchor=[ +1, +1 ], position = world.Place( +1, +1 ), text_bg=0, text_color=1, alpha=0.5 )
	def wrap_finish( gamma ):
		for name in 'gammatest gamma_readout'.split():
			stim = world.stimuli.get( name, None )
			if stim: stim.Leave()
		finish and finish( gamma )
	AdjustGamma( world, target=world.stimuli.gammatest, finish=wrap_finish )
	return world.stimuli.gammatest

def TearingTest( world, period_sec=4.0, proportional_width=0.15 ):
	"""
	Show a high-contrast bar oscillating from side to side, allowing visual
	inspection of possible "tearing" artifacts.
	"""
	#if 'canvas' not in world.stimuli: world.MakeCanvas()
	#world.stimuli.canvas.bg = 0
	width = max( 100, int( math.ceil( world.width * proportional_width ) ) )
	xoffset, yoffset = world.Place( 0 )
	bar = world.Patch(
		name = 'tearingtest',
		z = -1.0,
		width = width,
		height = world.height,
		anchor = world,
		signalFunction = 1,
		sigf = 2.0 / width,
		siga = 1000,
		bg = 0.5,
		fg = 1.0,
		outOfRangeColor = -1,
		outOfRangeAlpha = -1,
		x = lambda t: xoffset + 0.5 * world.width * math.sin( 2.0 * math.pi * t / period_sec ),
	)
	return bar

def GetTimings( world, nFrames=None, startFrame=None, stopFrame=None, key='DrawTimeInMilliseconds' ):
	a = world.timings.get( key, None )
	if a is None: return []
	bufferSize = len( a )
	maxStopFrame = world.framesCompleted
	maxNFrames = min( bufferSize, maxStopFrame )
	minStartFrame = maxStopFrame - maxNFrames
	if nFrames is not None and not ( 0 <= nFrames <= maxNFrames ):
		raise ValueError( 'cannot return an array of %r frames (%r frames available)' % ( nFrames, maxNFrames ) ) 
	if startFrame is not None and not ( minStartFrame <= startFrame < maxStopFrame ):
		raise ValueError( 'cannot query frame %r --- frame unavailable' % startFrame )
	if stopFrame  is not None and not ( minStartFrame <= stopFrame <= maxStopFrame ):
		raise ValueError( 'cannot query frame %r --- frame unavailable' % ( stopFrame - 1 ) )
	if stopFrame  is None: stopFrame  = maxStopFrame if ( startFrame is None or nFrames is None ) else min( maxStopFrame, startFrame + nFrames )
	if startFrame is None: startFrame = minStartFrame if ( stopFrame is None or nFrames is None ) else max( minStartFrame, stopFrame - nFrames )
	startFrame %= bufferSize
	stopFrame %= bufferSize
	if startFrame <= stopFrame:
		return a[ startFrame : stopFrame ]
	else:
		earlier, later = a[ startFrame: ], a[ :stopFrame ]
		return numpy.concatenate( ( earlier, later ), axis=0 ) if numpy else earlier + later

def EstimateFrameRate( world, nIdentical=10, nMaxFrames=100, nWarmUpFrames=10, threshold=1, wait=True ):
	"""
	DOC-TODO
	"""
	wr = weakref.ref( world )
	attributeName = 'estimatedFrameRate'
	nTries = [ 0 ]
	numpy.array # raises an informative exception if numpy not installed
	def FrameRateEstimator( _ ):
		world = wr()
		if not world: return
		if world.framesCompleted < nWarmUpFrames + nIdentical: return
		msec = GetTimings( world, nFrames=nIdentical, key='DrawTimeInMilliseconds' )
		msec = numpy.diff( msec )
		if numpy.std( msec ) <= threshold:
			raise StopIteration( 1000.0 / numpy.median( msec ) )
		nTries[ 0 ] += 1
		if nTries[ 0 ] >= nMaxFrames:
			raise StopIteration( float( 'nan' ) )
	world.SetDynamic( attributeName, FrameRateEstimator )
	if world.state == 'running' and wait: 
		world.WaitFor( attributeName )
		answer = getattr( world, attributeName )
		if answer != answer: raise RuntimeError( 'could not get a stable frame-rate estimate' )
		return answer
	
	
def RelativeLocation( loc, obj, anchor=None, normalized=False ):
	"""
	Translate a two-dimensional location `loc`...
	
	From:
	    `World` coordinates (i.e. pixels relative to the `World`'s current
	    `.anchor` position)
	To:
	    coordinates relative to the current `.xy` position of a `Stimulus`
	    instance in the same `World`, or (optionally) relative to a different
	    `.anchor` position of the `Stimulus` instance.
	
	Args:
	    loc:
	        input coordinates, in pixels (single scalar or sequence of two scalars)
	
	    obj:
	        `Shady.Stimulus` or `Shady.World` instance
	
	    anchor:
	        By default, the return value is expressed as an offset in pixels
	        relative to the anchor position of `obj` (so, if obj is a `Stimulus`,
	        the function just subtracts `obj.xy`; or if `obj` is the `World`, the
	        output value will be equal to the input value).However, if you specify
	        an explicit `anchor` (2 numbers each in the range `[-1, +1]`) then the
	        return value will be re-expressed as a pixel offset relative to some
	        other part of `obj`.  For example, with `anchor=[-1,-1]` you would get
	        pixel coordinates relative to the bottom left corner of `obj`, or with
	        `anchor=[0,+1]` you get pixel coordinates relative to the middle of the
	        top edge of `obj`.  The `anchor` argument is ignored if you specify
	        `normalized=True`.
	    
	    normalized (bool):
	        If `False`, return 2-D coordinates in pixels. If `True`, ignore `anchor`
	        and return 2-D coordinates in the normalized coordinate system of `obj`.
	        This effectively makes this function the inverse of `obj.Place()`.
	       
	Returns:
	    `[x, y]` coordinates, in pixels or normalized units depending on the
	    `normalized` argument.
	
	See also:
	    - `Stimulus.Place()`
	    - `World.Place()`
	
	"""
	try: x, y = loc.x, loc.y
	except: x, y = loc
	w, h = obj.size
	try: x0, y0 = obj.xy
	except: x0 = y0 = 0.0
	x, y = float( x ), float( y )
	
	pt = lambda v, n: math.floor( ( 0.5 + 0.5 * n ) * v )
	x -= x0 
	y -= y0
	if normalized or anchor is not None:
		x -= pt( -w, obj.anchor[ 0 ] ) 
		y -= pt( -h, obj.anchor[ 1 ] )
	if normalized:
		x = 2 * x / w - 1.0
		y = 2 * y / h - 1.0
	elif anchor is not None:
		try: xp, yp = anchor
		except: xp = yp = anchor
		x += pt( -w, xp )
		y += pt( -h, yp )
	if numpy: return numpy.array( [ x, y ] )
	return [ x, y ]

def PixelRuler( base, steps=((10,(0,0,1)), (100,(1,0,0)), (1000,(0,1,0))), alpha=None, topDown=False, world=None, oscillateGamma=False ):
	"""
	If `base` is an image size specification, or a `World` instance,
	create a 90%-contrast gray `CheckPattern()` of the appropriate size,
	to use as a base.  Alternatively, `base` may be a ready-made image.
	
	Draw grid lines over the base: the first pixel (pixel 0) is not colored.
	The 10th, 20th, 30th,... pixels (i.e. pixels 9, 19, 29, ...) are blue.
	Similarly every 100th pixel is red, and every 1000th pixel is green.
	
	The `topDown` argument changes the definition of "first pixel": the
	default is `topDown=False`, which means the first pixel is the bottom
	row and we work upwards, just like Shady's normal coordinate system.
	But if you specify  `topDown=True`, the first pixel is on the top row
	and we work downwards (the way one would index rows of a matrix).
	
	If `base` is a `World` instance, or if `world` is supplied as a separate
	argument, render the pattern at a depth of `z=0.9` and return the
	corresponding `Stimulus` instance. Otherwise just return the texture as
	a `numpy` array.
	
	When rendering as a stimulus, the `oscillateGamma` argument may be
	useful. Non-zero values cause the stimulus `.gamma` property to oscillate
	between 1.0 and 3.0 as a function of time. The pixel values set by
	`PixelRuler`, as well as those of the underlying default `CheckPattern`,
	are all either 1.0 or 0.0---therefore, changes in `.gamma` should not
	be visible. The oscillation *becomes* visible if there is any spatial
	interpolation of pixel values, so it is a useful tool for highlighting
	any unintended geometric anomalies that violate the pixel-for-pixel
	assumption (sub-pixel shifts, non-90-degree rotations, scaling).
	"""
	
	steps = sorted( dict( steps ).items() )
	
	if hasattr( base, '_isShadyObject' ): world = base.world()
	if world and base is None: base = world
	try: w, h = AsSize( base, False )
	except: img = numpy.array( base, copy=True )
	else:
		w = ( [ w ] + [ step for step, color in steps if step <= w ] )[ -1 ]
		h = ( [ h ] + [ step for step, color in steps if step <= h ] )[ -1 ]
		img = CheckPattern( ( w, h ), 0.9, meanZero=False )
		if alpha is not None:
			img = numpy.concatenate( ( img[ :, :, None ], img[ :, :, None ] * 0 + alpha ), axis=2 )
		if world and not hasattr( base, '_isShadyObject' ): base = world
	if world: world = world.world()
	
	if img.dtype == 'uint8': img = img / 255.0
	if img.ndim == 2: img = img[ :, :, None ]
	if img.shape[ 2 ] == 1: img = img[ :, :, [ 0, 0, 0 ] ]
	if img.shape[ 2 ] == 2: img = img[ :, :, [ 0, 0, 0, 1 ] ]
	if alpha is not None and img.shape[ 2 ] == 3:
		img = numpy.concatenate( ( img, img[ :, :, :1 ] * 0 + 1 ), axis=2 )
	h, w = img.shape[ :2 ]
	for step, color in sorted( dict( steps ).items() ):
		rows = range( step - 1, h, step ) if topDown else range( h - step, -1, -step )
		cols = range( step - 1, w, step )
		for pos in rows:
			for channel, value in enumerate( color ): img[ pos, :, channel ] = value
			img[ pos, :, 3:4 ] = 1.0 if alpha is None else alpha # alpha, if img has it
		for pos in cols:
			for channel, value in enumerate( color ): img[ :, pos, channel ] = value
			img[ :, pos, 3:4 ] = 1.0 if alpha is None else alpha # alpha, if img has it
	
	if world:
		if base is world or not hasattr( base, '_isShadyObject' ):
			stim = world.Stimulus( img, name='pixelruler', z=0.99, size=world.size, anchor=world )
		else:
			stim = base
			stim.LoadTexture( img, updateEnvelopeSize=False )
			stim.Set( carrierTranslation=0, carrierRotation=0, carrierScaling=1 )
		if topDown:
			stim.cy = base.height - h
		if oscillateGamma:
			omega = 2 * math.pi * float( oscillateGamma )
			stim.gamma = lambda t: math.sin( t * omega ) + 2
		return stim
	else: return img

def Cross( world=None, size=13, thickness=3, **props ):
	"""
	Create an image of a simple cross (horizontal and vertical strokes) and
	optionally render it as a `Stimulus` object.
	
	Args:
		world (World):
			Optional.  If supplied, the image will be rendered as a `Stimulus`
			with `z=-0.9` and `linearMagnification=False`.  If omitted, the
			function will simply return the array of pixel values.
	
		size (int):
			Desired dimensions of the final image, in pixels. For symmetry, if
			`thickness` is odd, `size` should also be odd; and if `thickness` is
			even, `size` should also be even. Otherwise `size` will get reduced
			by 1.
		
		thickness (int):
			Thickness of the strokes of the cross, in pixels.
		
		**props:
			Optional properties to be applied to the `Stimulus` object (ignored
			if `world` is not supplied).
	
	Returns:
		If a `World` instance `world` is supplied, returns a `Stimulus` instance.
		Otherwise just return the array of pixel values.
	"""
	width, height = AsSize( size, True )
	xthickness, ythickness = AsSize( thickness, False )
	xlength = max( 0, int( ( width  - xthickness ) / 2 ) )
	ylength = max( 0, int( ( height - ythickness ) / 2 ) )
	one  = [ 1., 1. ] # luminance, alpha
	zero = [ 0., 0. ] # luminance, alpha
	horizontal = [ one ] * ( xlength + xthickness + xlength )
	vertical = [ zero ] * xlength + [ one ] * xthickness + [ zero ] * xlength
	img = [ vertical ] * ylength + [ horizontal ] * ythickness + [ vertical ] * ylength
	if world: return world.Stimulus( img, name='cross%02d', z=-0.9, linearMagnification=False ).Set( **props )
	else: return img

def GridLines( size, steps=( ( 10, ( 0, 0, 1 ) ), ( 100, ( 1, 0, 0 ) ), ( 1000, ( 0, 1, 0 ) ) ), returnType='auto', **stimulusConstructorArguments ):
	# Helper function for FrameIntervalGauge
	# Returns a list of items, one item for each item in the input argument `steps`.
	# The type of the items may vary according to the desired `returnType`.
	# 
	# From `GridLines( size )` or equivalently `GridLines( world, returnType='points' )`
	# each item in the output list is a list of complex numbers suitable for assigning
	# to the `.points` property of a `Stimulus` in order to draw regularly-spaced grid
	# lines.
	# 
	# With `returnType='dict'`,  each item becomes a `dict` containing all the properties
	# (including `.points`) that you would need to assign to a `Stimulus` if you wanted
	# to draw the lines.
	# 
	# With `returnType='stimuli'`,  which is assumed by default in `GridLines( target )`
	# if `target` is a `Shady.World` or `Shady.Stimulus` instance, each returned item is
	# a newly-created `Stimulus` instance could be used to overlay grid lines on the
	# specified target.  You may wish to specify additional `**stimulusConstructorArguments`.
	
	if hasattr( size, '_isShadyObject' ):
		world = size.world() # weakref de-ref
		if returnType == 'auto': returnType = 'stimuli'
	else:
		world = None
		if returnType == 'auto': returnType = 'points'
	width, height = AsSize( size, True )
	if isinstance( steps, ( int, float ) ): steps = [ steps ]
	if isinstance( steps, ( tuple, list ) ): steps = [ x if isinstance( x, ( tuple, list ) ) else ( x, -1 ) for x in steps ]
	if isinstance( steps, dict ): steps = sorted( steps.items() )
	xstop, ystop = width - 1, ( height - 1 ) * 1j
	result = [
		[
			x + y
			for x in range( step - 1, width, step )
			for y in [ 0, ystop ]
		] + [
			x + y * 1j
			for y in range( step - 1, height, step )
			for x in [ 0, xstop ]
		]
		for step, color in steps
	]
	if returnType == 'points': return result
	
	result = [ dict(
		size = ( width, height ),
		color = color,
		drawMode = 3,  # Shady.DRAWMODE.LINES,
		smoothing = 1,
		penThickness = 1,
		points = points,
		ditheringDenominator = -1,
	) for ( step, color ), points in zip( steps, result ) ]
	if returnType == 'dicts': return result
	
	if returnType != 'stimuli': raise ValueError( 'returnType=%r unrecognized' % returnType )
	if world is None: raise ValueError( 'for returnType=%r you must supply Stimulus or World instance as first argument' % returnType )
	for args in result: args.update( stimulusConstructorArguments )
	result = [ world.Stimulus( **args ) for args in result ]
	return result
	

class FrameIntervalGauge( object ):
	"""
	Display an animated gauge that visually records the frame-to-frame
	interval in milliseconds.  Every millisecond is marked in blue;
	every ten milliseconds in red.  To avoid overhead, no text is rendered.
	"""
	def __init__( self, world, corner=( -1, -1 ), thickness=49, variable='width', color=( 0, 0, 0 ), useTexture=True ):
			
		fgColor = color
		bgColor = [ 1, 1, 1 ]
		steps = { 10:[0,0,1], 100:[1,0,0], 1000:[0,1,0] }
		dims = [ 1000, thickness ]
		if variable == 'height': dims = dims[ ::-1 ]

		if not numpy: useTexture = False
		if useTexture:
			base = numpy.ones( dims[ ::-1 ] + [ 3 ], dtype=float )
			bgTexture = PixelRuler( base * [ [ bgColor ] ], steps=steps )
			fgTexture = PixelRuler( base * [ [ fgColor ] ], steps=steps )
				
		namingPattern = 'gauge%02d'
		def Make():
			ruler = world.Stimulus(
				bgTexture if useTexture else None,
				name = namingPattern,
				debugTiming = False,
				position = world.Place( corner ),
				anchor = corner,
				z = -0.999,
				size = dims,
				ditheringDenominator = -1,
				color = -1 if useTexture else bgColor,
				#alpha = 0.5,
			)
			shared = dict( position=ruler, anchor=ruler, z=ruler, visible=ruler, ditheringDenominator=ruler )
			bar = world.Stimulus(
				fgTexture if useTexture else None,
				name = namingPattern,
				debugTiming = False,
				size = dims,
				color = -1 if useTexture else fgColor,
				**shared
			)
			grids = [] if useTexture else GridLines( ruler, name=namingPattern, **shared )
			return ruler, bar, grids
			
		self.world = world
		self.variableDimension = variable
		self.ruler, self.bar, self.grids = world.RunDeferred( Make )
		self.ruler.SetAnimationCallback( self.Animate )
		
	def Animate( self, unusedTimeArgument ):
		world = self.world
		
		fr = world.framesCompleted
		msec = getattr( world, 'timings' ).get( 'DrawTimeInMilliseconds', None )		
		if msec is not None:
			bufferSize = len( msec )
			latest = msec[ fr % bufferSize ]
			previous = msec[ ( fr - 1 ) % bufferSize ]
			msec = ( latest - previous )
			if msec != msec: msec = None
		if msec is None: barLengthInMsec, rulerLengthInMsec =    1, 50
		else:            barLengthInMsec, rulerLengthInMsec = msec, 50   # math.ceil( msec / 40.0 ) * 40.0
		
		ruler, bar, grids = self.ruler, self.bar, self.grids
		variable = self.variableDimension
		
		setattr( ruler, variable, int( round( rulerLengthInMsec * 10 ) ) )
		setattr( bar,   variable, int( round( barLengthInMsec   * 10 ) ) )
		if grids:
			rw, rh = ruler.size
			bw, bh = bar.size
			targetSize = max( rw, bw ), max( rh, bh )
			if tuple( grids[ 0 ].size ) != targetSize:
				for grid, points in zip( grids, GridLines( targetSize ) ):
					grid.size = targetSize
					grid.points = points 
		
		
	
def Loupe( target, update_period=1.0, **kwargs ):
	"""
	Given a `target` instance of class `Stimulus`, create another `Stimulus`
	instance that presents a magnified, contrast-enhanced, slowed-down (or
	rather, temporally sub-sampled) view of the pixels rendered by the
	`target`.
	
	The returned instance has the following additional attributes:
	
	    * `.target`: a `weakref.ref` to the `target` instance
	    * `.update_period`: a floating-point number of seconds
	    * `.update_now`: a boolean which, if set to `True`, forces an
	      update on the next frame (and which is then automatically
	      set back to `False`).
	
	NB: raw (post-linearization) pixel values are captured from the
	target and then rendered on the loupe which is itself, necessarily,
	*unlinearized*.  At extreme values, color-contrast-enhancement may
	therefore lead to an apparent change in mean luminance even though
	there is no such change in the target.
	"""
	world = target.world()
	enhanced = world.Stimulus(
		name = 'loupe',
		size = target.size,  #  no need to link these:
		bg = target.bg,      #   they will be updated in Animate() below
		outOfRangeColor = -1,
		cyscaling = -1,
		gamma = 1,
		scaling = 4,
		linearMagnification = 0,
	)
	enhanced.Set( **kwargs )
	enhanced.target = weakref.ref( target )
	enhanced.update_period = update_period
	enhanced.update_now = 'defer'
	enhanced.dacMax = float( world.GetPropertyDescriptor( 'ditheringDenominator' ).default[ 0 ] )
	if enhanced.dacMax <= 0.0: enhanced.dacMax = 255.0
	def Animate( self, t ):
		"""
		Note that this callback updates the loupe stimulus's `.size`,
		`.backgroundColor` and `.normalizedContrast` on every frame,
		according to its own logic. However if you want to take direct
		control of `.backgroundColor` and/or `.normalizedContrast`
		yourself, you can signal this by assigning dynamic values to
		them. Note that in the case of `.backgroundColor` you may wish
		to `Linearize()` the value you're using in your dynamic, since
		the loupe stimulus itself is rendered with linear gamma.
		"""
		if self.world().framesCompleted < 1: return
		triggered = ( t > self.update_period )
		if self.update_now == 'defer': self.update_now = True # but don't trigger this time
		elif self.update_now: triggered = True
		if triggered:
			target = self.target
			if isinstance( target, weakref.ReferenceType ): target = target()
			if target:
				if self.textureSlotNumber < 0 or self.textureID < 0 or list( target.size ) != list( self.textureSize ):
					self.LoadTexture( target.Capture() ) # this is a bit of a hack (and it introduces a dependency on numpy) but it's by far the easiest way of initializing everything correctly
				target.CaptureToTexture( self.textureID )
				if not self.GetDynamic( 'bg' ):
					if target.lut: self.bg = ApplyLUT( target.bgred, target.lut.values ) / self.dacMax
					else: self.bg = [ Linearize( bg, gamma ) for bg, gamma in zip( target.bg, target.gamma ) ]
				if not self.GetDynamic( 'contrast' ):
					headroom = [ min( val, 1.0 - val ) for val in self.bg ]
					self.contrast = 2.0 * max( headroom ) / target.contrast # 20 minutes into the future
			self.ResetClock()
			self.update_now = False
	enhanced.SetAnimationCallback( Animate )
	wr = weakref.ref( enhanced )
	enhanced.DeferredUpdate = lambda: setattr( wr(), 'update_now', 'defer' )
	return enhanced

# plotting
def PlotTimings( arg, savefig=None, traces=(), axes=None, finish=True, **kwargs ):
	"""
	Plot a graph of the recent timing diagnostics from a `World` instance or
	log-file name.
	
	The information is richer if the `World` instance, and even more so if
	individual `Stimulus` instances, had `.debugTiming` set to True.
	
	Requires the third-party packages `numpy` and `matplotlib`.
	"""
	if arg is sys.argv:
		cmdline = CommandLine( arg[ 1: ] )
		arg     = cmdline.Option( 'arg', type=str, position=0 )
		savefig = cmdline.Option( 'savefig', savefig, type=( str, None ) )
		traces  = cmdline.Option( 'traces',  traces,  type=( str, tuple, list ) )
		cmdline.Finalize()
	
	if isinstance( arg, str ): output, timings = None, Logging.Read( arg )[ 'timings' ]
	elif isinstance( arg, dict ) and 'timings' in arg: output, timings = None, arg[ 'timings' ]
	elif hasattr( arg, 'timings' ): output, timings = arg, arg.timings
	else: output, timings = None, arg
	
	if isinstance( traces, str ): traces = traces.replace( ',', ' ' ).split()
	traces = { key.split( '=' )[ 0 ].strip() : [ i, key.split( '=', 1 )[ 1 ].strip() if '=' in key else key ] for i, key in enumerate( traces ) }
	try: nanmean = numpy.nanmean
	except AttributeError: nanmean = lambda x: x[ ~numpy.isnan( x ) ].mean()
	sortkey = lambda item: [ traces.get( item[ 0 ], [ 0 ] )[ 0 ], -nanmean( item[ 1 ] ) ]
	
	plt = DependencyManagement.LoadPyplot()
	plt.plot # trigger exception if not found 
	with warnings.catch_warnings():
		warnings.filterwarnings( 'ignore', message='invalid value encountered in' )
		processed = {}
		cpu = False
		t = numpy.asarray( timings[ 'DrawTimeInMilliseconds' ] ) / 1000.0
		keep = ~numpy.isnan( t )
		t = t[ keep ]
		reorder = numpy.argsort( t )
		t = t[ reorder ]
		t = t - t[ 0 ]
		for key, value in timings.items():
			value = numpy.asarray( value )[ keep ][ reorder ].copy()
			if key == 'DrawTimeInMilliseconds':
				value = numpy.diff( value.tolist() + [ numpy.nan ] )
				key = 'Delta' + key
				value[ value > 1000.0 ] = numpy.inf
				value[ value < 0.0 ] = 0.0
			if traces and key not in traces: continue
			processed[ key ] = value
			if key.startswith( 'cpu_' ):
				cpu = True
				smoothing = 0.9
				for i in range( 1, value.size ):
					value.flat[ i ] = smoothing * value.flat[ i - 1 ] + ( 1.0 - smoothing ) * value.flat[ i ]
		if axes:
			plt.sca( axes )
			ax1 = ax2 = plt.gca()
		else:
			plt.clf()
			if cpu: ax1 = plt.subplot( 2, 1, 1 ); ax2 = plt.subplot( 2, 1, 2, sharex=ax1 )
			else: ax1 = plt.gca(); ax2 = None
		for i, ( key, value ) in enumerate( sorted( processed.items(), key=sortkey ) ):
			if key.startswith( 'cpu' ): style = '-'; plt.sca( ax2 )
			else: style = '-'; plt.sca( ax1 )
			if key in traces: _, label = traces[ key ]
			else: label = '%02d %s' % ( i, key )
			plt.plot( t, value, style, label=label, **kwargs )
		
		def make_draggable( legend, setting=True ):
			try: legend.set_draggable( setting )
			except: legend.draggable( setting )
				
		if ax1: plt.sca( ax1 ); plt.grid( True ); plt.xlim( [ t.min(), t.max() ] ); make_draggable( plt.legend( loc=( 1.01, -1 if cpu else 0 ), labelspacing=0 ) )
		if ax2: plt.sca( ax2 ); plt.grid( True ); plt.xlim( [ t.min(), t.max() ] ); make_draggable( plt.legend( loc=( 1.01, 0 ), labelspacing=0 ) )
		plt.gcf().subplots_adjust( right=0.8 )
		if finish: FinishFigure( maximize=True, raise_=True, zoom=True, savefig=savefig, wait=( finish if finish in [ 'block' ] else None ) )
	return output

def Histogram( img, plot=True, DACmax=255, title=None, xlabel='Red, Green or Blue DAC Value', ylabel='Number of Pixels' ):
	"""
	Takes an array of pixel values (for example, a `Stimulus.Capture()` output)
	and computes histograms of the luminance values in each channel. Optionally,
	plots the histograms.
	
	Requires the third-party package `numpy` to compute histograms, and
	`matplotlib` if you want to plot them.
	"""
	if plot:
		plt = DependencyManagement.LoadPyplot()
		plt.plot # trigger exception if not found 
	
	if hasattr( img, 'Capture' ): img = img.Capture()
	if img.dtype == float:
		if img.min() < 0: img = 0.5 + 0.5 * img
		dtype = 'uint8' if DACmax == 255 else int
		img = numpy.clip( img * DACmax, 0.0, DACmax ).astype( dtype )
	if img.ndim == 2: img = img[ :, :, None ]
	x = numpy.arange( DACmax + 1 ) # 0 to 255 inclusive
	bin_edges = numpy.arange( DACmax + 2.0 ) - 0.5   # -0.5 to 255.5 inclusive (includes rightmost edge)
	hist = lambda a: numpy.histogram( a.flat, bins=bin_edges )[ 0 ]
	if plot: plt.cla()
	results = {}
	if img.shape[ 2 ] in [ 1, 2 ]:
		result = results[ 'L' ] = hist( img[ :, :, 0 ] ); plot and plt.plot( x, result, color='k', marker='s', clip_on=False )
	else:
		result = results[ 'R' ] = hist( img[ :, :, 0 ] ); plot and plt.plot( x, result, color='r', marker='o', clip_on=False )
		result = results[ 'G' ] = hist( img[ :, :, 1 ] ); plot and plt.plot( x, result, color='g', marker='x', clip_on=False )
		result = results[ 'B' ] = hist( img[ :, :, 2 ] ); plot and plt.plot( x, result, color='b', marker='+', clip_on=False )
	if plot:
		plt.xlim( x[ [ 0, -1 ] ] )
		plt.ylim( [ 0, max( plt.ylim() ) ] )
		plt.grid( True )
		if title: plt.title( title )
		if xlabel: plt.xlabel( xlabel )
		if ylabel: plt.ylabel( ylabel )
	return results


def FinishFigure( maximize=False, raise_=False, pan=False, zoom=False, wait=None, savefig=None ):
	plt = DependencyManagement.LoadPyplot()
	if not plt or not plt.get_fignums(): return
	IPython, iPythonShellInstance, ipythonIsRunning = GetIPython()
	if wait is None: wait = not ipythonIsRunning
	if ipythonIsRunning: plt.ion()
	elif wait: plt.ioff()
	plt.draw()
	try: toolbar = plt.gcf().canvas.toolbar
	except: toolbar = None
	if pan and toolbar is not None:
		try: turn_on_pan = ( toolbar._active is not 'PAN' )
		except: turn_on_pan = True
		if turn_on_pan: toolbar.pan( 'on' )
	if zoom and toolbar is not None:
		try: turn_on_zoom = ( toolbar._active is not 'ZOOM' )
		except: turn_on_zoom = True
		if turn_on_zoom: toolbar.zoom( 'on' )
	try: manager = plt.get_current_fig_manager()
	except: manager = None
	if maximize:
		try: plt.gcf().canvas._tkcanvas.master.wm_state( 'zoomed' )
		except: pass
		try: manager.window.state( 'zoomed' )
		except: pass
		try: manager.window.showMaximized()
		except: pass
		try: manager.frame.Maximize( True )
		except: pass
	if raise_:
		try: manager.window.raise_()
		except: pass
	if savefig: plt.gcf().savefig( savefig )
	if wait == 'block': plt.show( block=True )
	elif wait: plt.show()


# visual arc wrangling

RADIANS_PER_DEGREE = math.pi / 180.0

def _ReadFileInto( filename, d ):
	exec( open( arg, 'rt' ).read(), dict( nan=float( 'nan' ), inf=float( 'inf' ) ), d )

def _StandardizeName( k ):
	k = k.lower().replace( '_', '' ).replace( ' ', '' ).replace( '(', '' ).replace( ')', '' )
	return k[ 6: ] if k.startswith( 'screen' ) else k
		
def _GetSetting( src, stem, **suffixes ):
	sstem = _StandardizeName( stem )
	factors = { sstem + joiner + k : v for k, v in suffixes.items() for joiner in [ '', 'in' ] }
	matched = {}
	for key, value in src.items():
		factor = factors.get( _StandardizeName( key ), None )
		if factor is not None and value is not None: matched[ key ] = value * factor
	if not matched: return float( 'nan' )
	if len( set( matched.values() ) ) > 1: raise ValueError( 'conflicting %s information: %s' % ( stem, ', '.join( '%s=%s' % ( k, src[ k ] ) for k in matched ) ) )
	return float( list( matched.values() )[ 0 ] )

def VDP( *pargs, **kwargs ):
	"""
	Return viewing distance measured in pixels, based on a set of configuration parameters.
	This allows easy conversion between degrees and pixels.
	
	If a single scalar numeric argument is provided, return it unchanged.
	
	If a string is provided, treat it the name of a Python file which defines the necessary
	settings as variables, and execute it.
	
	If a `Shady.World` object is provided, infer `widthInPixels` and `heightInPixels` from
	its size. Otherwise, if a `dict` is provided, take the necessary settings from that.
	
	Use `**kwargs` to augment / override settings.

	The necessary settings are:
	
	* `viewingDistanceInMm`,  and
	
	* EITHER:   `widthInPixels`   AND  `widthInMm`
		  OR:   `heightInPixels`  AND  `heightInMm`
	
	Flexibility is allowed with these variable names: they are case-invariant and
	underscore-invariant, the `'In'` is optional, and the physical units can be mm, cm or
	m. So for example::
	
		viewing_distance_cm = 75
		
	would give the same result as::
	
		ViewingDistanceInMm = 750
	
	Example::
	
		v = VDP( world, heightInMm=169, viewingDistanceInCm=75 )
		pixelsPerDegree = DegreesToPixels( 1.0, v )
	"""
	info = {}
	
	if pargs and isinstance( pargs[ 0 ], ( float, int ) ):
		if pargs[ 1: ] or kwargs: raise TypeError( "additional arguments cannot be used when the first input argument is numeric" )
		viewingDistanceInPixels = pargs[ 0 ]
		return viewingDistanceInPixels
				
	for arg in pargs + ( kwargs, ):
		if isinstance( arg, dict ): info.update( arg )
		elif isinstance( arg, str ): _ReadFileInto( arg, info )
		elif hasattr( arg, 'width' ) and hasattr( arg, 'height' ): info[ 'WidthInPixels' ], info[ 'HeightInPixels' ] = arg.width, arg.height
		else: raise TypeError( 'could not interpret input argument' )
		
	millimeters = dict( mm=1.0, millimeters=1.0, cm=10.0, centimeters=10.0, m=1000.0, meters=1000.0, )
	pixels = dict( pixels=1.0 )
	
	widthInPixels  = _GetSetting( info, 'width',  **pixels )
	widthInMm      = _GetSetting( info, 'width',  **millimeters )
	heightInPixels = _GetSetting( info, 'height', **pixels )
	heightInMm     = _GetSetting( info, 'height', **millimeters )
	viewingDistanceInMm  = _GetSetting( info, 'viewing distance', **millimeters )
	
	if math.isnan( viewingDistanceInMm ):
		raise ValueError( 'need information about viewing distance, e.g.  ViewingDistanceInCm=75' )
	if math.isnan( widthInMm ) and math.isnan( heightInMm ):
		raise ValueError( 'need information about physical display size, e.g.  widthInMm=254, heightInMm=169' )
	if math.isnan( widthInPixels ) and math.isnan( heightInPixels ):
		raise ValueError( 'need information about pixel dimensions, e.g.  widthInPixels=2160, heightInPixels=1440' )
	mmPerPixelHorizontally = widthInMm  / widthInPixels
	mmPerPixelVertically   = heightInMm / heightInPixels
	if math.isnan( mmPerPixelHorizontally ) and math.isnan( mmPerPixelVertically ):
		raise ValueError( 'need both pixel and millimeter dimensions for at least one dimension, e.g.  heightInPixels=1440, heightInMm=169' )
	elif math.isnan( mmPerPixelHorizontally ):
		viewingDistanceInPixels = viewingDistanceInMm / mmPerPixelVertically
	elif math.isnan( mmPerPixelVertically ):
		viewingDistanceInPixels = viewingDistanceInMm / mmPerPixelHorizontally
	else:
		viewingDistanceInPixels = viewingDistanceInMm / ( 0.5 * mmPerPixelHorizontally + 0.5 * mmPerPixelVertically )
		aspectRatio = mmPerPixelHorizontally / mmPerPixelVertically
		if aspectRatio < 0.95 or aspectRatio > 1.05: raise ValueError( 'conflicting screen dimension settings: the specified horizontal and vertical resolutions imply non-square pixels (aspect ratio %g)' % aspectRatio )
	return viewingDistanceInPixels
	
def DegreesToPixels( extentInDegrees, screenInfo, eccentricityInDegrees=0 ):
	"""
	Compute the extent of a stimulus in pixels, given the number of degrees
	of visual arc it subtends and its eccentricity in degrees away from
	the line of sight.
	
	Args:
		extentInDegrees:
			an `int`, `float` or sequence/array of numbers, denoting the
			number of degrees subtended at the eye by the stimulus.
		screenInfo:
			either the input (a filename or a `dict`) or the output (a
			floating-point number) of `VDP()`.
		eccentricityInDegrees:
			an `int`, `float` or sequence/array of numbers, denoting the
			angle in degrees between the line of sight and the line from
			the eye to the center of the stimulus
	
	Returns:
		a `float` (for scalar inputs) or a `numpy.array` (for array inputs)
		denoting stimulus extent(s) in pixels.
	
	See also:
		- `PixelsToDegrees()`
		- `VDP()`
	"""
	if numpy: tan = numpy.tan; extentInDegrees = numpy.asarray( extentInDegrees ); eccentricityInDegrees = numpy.asarray( eccentricityInDegrees )
	else:     tan = math.tan
	viewingDistanceInPixels = VDP( screenInfo )
	startInDegrees = eccentricityInDegrees - extentInDegrees / 2.0
	endInDegrees   = eccentricityInDegrees + extentInDegrees / 2.0
	startInPixels = viewingDistanceInPixels * tan( startInDegrees * RADIANS_PER_DEGREE  )
	endInPixels   = viewingDistanceInPixels * tan( endInDegrees   * RADIANS_PER_DEGREE )
	#eccentricityInPixels   = viewingDistanceInPixels * tan( eccentricityInDegrees * RADIANS_PER_DEGREE  )
	extentInPixels = endInPixels - startInPixels
	if numpy and not extentInPixels.shape: extentInPixels = extentInPixels.flat[ 0 ]
	return extentInPixels

def PixelsToDegrees( extentInPixels, screenInfo, eccentricityInPixels=0 ):
	"""
	Compute the number of degrees of visual angle subtended by a stimulus of
	given its extent in pixels, and its distance from the point of fixation
	in pixels.
	
	Args:
		extentInPixels:
			an `int`, `float` or sequence/array of numbers, denoting the
			size of the stimulus in pixels.
		screenInfo:
			either the input (a filename or a `dict`) or the output (a
			floating-point number) of `VDP()`.
		eccentricityInPixels:
			an `int`, `float` or sequence/array of numbers, denoting the
			distance between fixation and the center of the stimulus, in
			pixels.
	
	Returns:
		a `float` (for scalar inputs) or a `numpy.array` (for array inputs)
		denoting angle(s) subtended, in degrees of visual arc. 
	
	See also:
		- `DegreesToPixels()`
		- `VDP()`
	"""
	if numpy: atan2 = numpy.arctan2; extentInPixels = numpy.asarray( extentInPixels ); eccentricityInPixels = numpy.asarray( eccentricityInPixels )
	else:     atan2 = math.atan2
	viewingDistanceInPixels = VDP( screenInfo )
	startInPixels = eccentricityInPixels - extentInPixels / 2.0
	endInPixels   = eccentricityInPixels + extentInPixels / 2.0
	startInDegrees = atan2( startInPixels, viewingDistanceInPixels ) / RADIANS_PER_DEGREE
	endInDegrees   = atan2( endInPixels,   viewingDistanceInPixels ) / RADIANS_PER_DEGREE
	#eccentricityInDegrees = atan2( eccentricityInPixels, viewingDistanceInPixels ) / RADIANS_PER_DEGREE
	extentInDegrees = endInDegrees - startInDegrees
	if numpy and not extentInDegrees.shape: extentInDegrees = extentInDegrees.flat[ 0 ]
	return extentInDegrees


# Contrast wrangling

def RMSContrastRatio( pixels, background=None ):
	r"""
	Compute the root-mean-square contrast ratio of a pixel array.
	:math:`\frac{\sqrt{\frac{1}{N}\sum_x\sum_y (L_{xy} - L_{\mu})^2}}{L_{\mu}}`,
	or in plain text::
	
	    (pixels - background).mean() ** 2 ) ** 0.5   /    background
	
	where `background` (:math:`=L_{\mu}`) defaults to `pixels.mean()`.
	
	If `pixels` is a three-dimensional array: if its extent in the third dimension
	is 2 or 4, the last layer is assumed to be an alpha channel and is excluded
	from the computation; then, the computation is based on the mean-across-channels
	but you *may* wish to convert your array into a single-channel array of
	luminances first, for more accurate results.
	
	This function will work on any kind of luminance scale: if you feed it ideal
	luminances (in the 0 to 1 range), you will get an "ideal" contrast ratio. If
	you feed it physical luminances (in candelas / m^2) you will get a physical
	contrast ratio. For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of `Shady.Documentation.LuminanceAndContrast`.
	
	See also:
		- `MichelsonContrastRatio()`
		- `IdealToPhysicalContrastRatio()`
		- `PhysicalToIdealContrastRatio()`
	"""
	pixels = numpy.array( pixels, dtype=float, copy=False )
	if pixels.ndim == 3:
		if pixels.shape[ 2 ] in [ 2, 4 ]: pixels = pixels[ :, :, ::-1 ]
		pixels = pixels.mean( axis=2 )
	if background is None: background = pixels.mean()
	return ( ( pixels - background ) ** 2 ).mean() ** 0.5 / background

def MichelsonContrastRatio( pixels, background=None ): # NB: background is unused
	r"""
	Compute the Michelson contrast ratio of a pixel array,
	:math:`\frac{L_{\max} - L_{\min}}{L_{\max} + L_{\min}}`,
	or in plain text::
	
	    (pixels.max() - pixels.min()) / (pixels.max() + pixels.min())
	
	The input argument `background` is unused but it is included in
	the prototype for compatibility with `RMSContrastRatio()`.
	
	If `pixels` is a three-dimensional array: if its extent in the third dimension
	is 2 or 4, the last layer is assumed to be an alpha channel and is excluded
	from the computation; then, the computation is based on the mean-across-channels
	but you *may* wish to convert your array into a single-channel array of
	luminances first, for more accurate results.
	
	This function will work on any kind of luminance scale: if you feed it ideal
	luminances (in the 0 to 1 range), you will get an "ideal" contrast ratio. If
	you feed it physical luminances (in candelas / m^2) you will get a physical
	contrast ratio. For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of `Shady.Documentation.LuminanceAndContrast`.
	
	See also:
		- `RMSContrastRatio()`
		- `IdealToPhysicalContrastRatio()`
		- `PhysicalToIdealContrastRatio()`
	"""
	pixels = numpy.array( pixels, dtype=float, copy=False )
	if pixels.ndim == 3:
		if pixels.shape[ 2 ] in [ 2, 4 ]: pixels = pixels[ :, :, ::-1 ]
		pixels = pixels.mean( axis=2 )
	pmin, pmax = pixels.min(), pixels.max()
	return ( pmax - pmin ) / ( pmax + pmin )

def _MakeArrayIfPossible( x, *pargs, **kwargs ):
	return numpy.array( x, *pargs, **kwargs ) if numpy else x
	
def IdealToPhysicalLuminance( idealLuminance, physicalScreenRange ):
	"""
	Convert ideal luminance (from 0 to 1) to physical luminance.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    idealLuminance:
	        "ideal" luminance value(s) to convert (in the range 0 to 1)
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Physical luminance value(s) corresponding to the ideal input
		value(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return screenPhysicalMin + ( screenPhysicalMax - screenPhysicalMin ) * _MakeArrayIfPossible( idealLuminance )

def PhysicalToIdealLuminance( physicalLuminance, physicalScreenRange ):
	"""
	Convert physical luminance to ideal luminance (from 0 to 1).
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    physicalLuminance:
	        physical luminance value(s) to convert
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Ideal luminance value(s) (in the range 0 to 1) corresponding to
		the physical input value(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return ( _MakeArrayIfPossible( physicalLuminance ) - screenPhysicalMin ) / ( screenPhysicalMax - screenPhysicalMin )

def IdealToPhysicalContrastRatio( idealContrastRatio, idealBackgroundLuminance, physicalScreenRange ):
	"""
	Convert one or more ideal contrast ratios to physical contrast ratios.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    idealContrastRatio:
	        "ideal" contrast ratio(s) to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Physical contrast ratio(s) corresponding to the ideal input
		value(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return _MakeArrayIfPossible( idealContrastRatio ) * idealBackgroundLuminance / ( idealBackgroundLuminance + screenPhysicalMin / float( screenPhysicalMax - screenPhysicalMin ) )

def PhysicalToIdealContrastRatio( physicalContrast, idealBackgroundLuminance, physicalScreenRange ):
	"""
	Convert one or more physical contrast ratios to ideal contrast ratios.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    physicalContrastRatio:
	        physical contrast ratio(s) to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	    physicalScreenRange:
	        sequence of [min, max] physical luminance values measured
	        from the screen with a photometer
	
	Returns:
		Ideal contrast ratio(s) corresponding to the physical input
		ratio(s).
	"""
	screenPhysicalMin, screenPhysicalMax = float( min( physicalScreenRange ) ), float( max( physicalScreenRange ) )
	return _MakeArrayIfPossible( physicalContrast ) / float( idealBackgroundLuminance ) * ( idealBackgroundLuminance + screenPhysicalMin / float( screenPhysicalMax - screenPhysicalMin ) )

def IdealContrastRatioToNormalizedContrast( idealContrastRatio, idealBackgroundLuminance ):
	"""
	Convert one or more ideal contrast ratios to normalized contrast scaling
	factors. For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    idealContrastRatio:
	        "ideal" contrast ratio(s) to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	Returns:
		Normalized contrast scaling factors(s) corresponding to the input
		ideal contrast ratio(s).
	"""
	return 2.0 * idealBackgroundLuminance * idealContrastRatio

def NormalizedContrastToIdealContrastRatio( normalizedContrast, idealBackgroundLuminance ):
	"""
	Convert one or more normalized contrast values to ideal contrast ratios.
	For more details, see :doc:`../auto/LuminanceAndContrast` in the
	online documentation or the docstring of
	`Shady.Documentation.LuminanceAndContrast`.
		
	Args:
	    normalizedContrast:
	        normalized contrast scaling factor(s) (in the range 0 to 1)
	        to convert
	
	    idealBackgroundLuminance:
	        "ideal" background luminance (scalar, in the range 0 to 1)
	
	Returns:
		Ideal contrast ratio(s) corresponding to the input normalized
		contrast scaling factor(s).
	"""
	return 0.5 * normalizedContrast / float( idealBackgroundLuminance )

def ContrastTest( normalizedContrast=1.0, idealBackgroundLuminance=0.5, physicalScreenRange=( 10.1, 221 ) ):
	idealLuminances = numpy.array( [ -1.0, +1.0, -1.0, +1.0, -1.0, +1.0 ] ) * 0.5 * normalizedContrast + idealBackgroundLuminance
	physicalLuminances = IdealToPhysicalLuminance( idealLuminances, physicalScreenRange )
	physicalBackgroundLuminance = IdealToPhysicalLuminance( idealBackgroundLuminance, physicalScreenRange )
	idealBackgroundLuminance_recon = PhysicalToIdealLuminance( physicalBackgroundLuminance, physicalScreenRange )
	print( [ idealBackgroundLuminance, idealBackgroundLuminance_recon ] )
	idealRMSContrastRatio = RMSContrastRatio( idealLuminances, idealBackgroundLuminance )
	physicalRMSContrastRatio = RMSContrastRatio( physicalLuminances, physicalBackgroundLuminance )
	idealRMSContrastRatio_recon = PhysicalToIdealContrastRatio( physicalRMSContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	physicalRMSContrastRatio_recon = IdealToPhysicalContrastRatio( idealRMSContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	print( [ idealRMSContrastRatio, idealRMSContrastRatio_recon ] )
	print( [ physicalRMSContrastRatio, physicalRMSContrastRatio_recon ] )
	idealMichelsonContrastRatio = MichelsonContrastRatio( idealLuminances, idealBackgroundLuminance )
	physicalMichelsonContrastRatio = MichelsonContrastRatio( physicalLuminances, idealBackgroundLuminance )
	idealMichelsonContrastRatio_recon = PhysicalToIdealContrastRatio( physicalMichelsonContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	physicalMichelsonContrastRatio_recon = IdealToPhysicalContrastRatio( idealMichelsonContrastRatio, idealBackgroundLuminance, physicalScreenRange )
	print( [ idealMichelsonContrastRatio, idealMichelsonContrastRatio_recon ] )
	print( [ physicalMichelsonContrastRatio, physicalMichelsonContrastRatio_recon ] )



def WorldConstructorCommandLine( argv=None, doc=None, **defaults ):
	"""
	This tool is used in our example scripts, and may be useful to you in
	any applications you write that are similarly launched from the
	command line. It creates a general-purpose `CommandLine` object, but
	then pre-configures various options to match the main arguments that
	can be passed to the `World` object constructor.
	
	Example::
	
		'Welcome to foo.py'
		import Shady
		
		cmdline = Shady.WorldConstructorCommandLine( canvas=True )
		# Add your own custom command-line option definitions here:
		hello = cmdline.Option( 'hello', default=False, type=bool, container=None ) 
		cmdline.Help().Finalize()
		
		world = Shady.World( **cmdline.opts )
		if hello:
			import Shady.Text
			greeting = world.Stimulus( text='Hello World!' )
		world.Run()
		
	In the above example, most of the `World` constructor arguments
	now have counterparts that can be passed on the command-line when
	you run `foo.py`. For example, if you say `python foo.py --screen=2`
	then the `World` will be opened on your second screen. If you say
	`python foo.py --help` then (thanks to the `.Help()` call above)
	the command-line arguments will be printed and then Python will
	exit without creating the `World`. The command-line arguments all
	have the same default values as their counterparts in the `World`
	constructor prototype, with one exception: `canvas` has had its
	default value explicitly changed to `True`.
	
	In the particular cases of `width` and/or `height`, they can be passed
	as named arguments (say, `python foo.py --width=1920 --height=1080`)
	or as positional arguments (`python foo.py 1920 1080`)
	
	If the `doc` argument is left as `None`, this function will
	impolitely ransack the calling namespace for a `__doc__` variable,
	and use that if it finds it.  Pass `doc=''` to suppress this.	
	"""
	if doc is None:
		try:
			frame = inspect.currentframe()
			doc = frame.f_back.f_locals.get( '__doc__', None )
		finally: del frame # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	cmdline = CommandLine( argv=argv, doc=doc )
	
	platform = sys.platform.lower()
	defaults.setdefault( 'threaded', platform.startswith( 'win' ) and Interactive() == 'main' )
	cmdline.Section( 'The usual World-construction arguments' )
	opt = lambda name, default, **spec: cmdline.Option( name, defaults.get( name, default ), **spec )
	opt( 'width',                default=None, position=0, type=( None, int, tuple, list ), min=1, minlength=2, maxlength=2 )
	opt( 'height',               default=None, position=1, type=( None, int ), min=1 )
	opt( 'size',                 default=None,  type=( None, int, tuple, list ), min=1, minlength=2, maxlength=2 )
	opt( 'left',                 default=None,  type=( None, int ) )
	opt( 'top',                  default=None,  type=( None, int ) )
	opt( 'screen',               default=None,  type=( None, int ), min=0 )
	opt( 'threaded',             default=True,  type=bool )
	opt( 'canvas',               default=False, type=( bool ) )
	opt( 'frame',                default=False, type=( bool ) )
	opt( 'fullScreenMode',       default=None,  type=( None, bool ) )
	opt( 'visible',              default=True,  type=( bool ) )
	opt( 'openglContextVersion', default=None,  type=( None, int ) )
	opt( 'legacy',               default=None,  type=( None, bool ) )
	opt( 'backend',              default=None,  type=( None, str ) )
	opt( 'acceleration',         default=None,  type=( None, bool, str ) )
	opt( 'debugTiming',          default=False, type=( bool ) )
	opt( 'profile',              default=False, type=( bool, str ), strings=[ 'profile', 'cProfile', 'hotshot', 'pyinstrument' ] )
	opt( 'syncType',             default=-1,    type=int, values=[ -1, 0, 1, 2, 3 ] )
	opt( 'logfile',              default=None,  type=( None, str ) )
	opt( 'reportVersions',       default=False, type=( bool ) )
	cmdline.Section( 'Other arguments' )
	
	if cmdline.opts[ 'fullScreenMode' ] is None and platform.startswith( 'darwin' ) and Interactive() == 'threaded':
		cmdline.opts[ 'fullScreenMode' ] = False
		print( """
NB: as we are in interactive mode, `fullScreenMode` is being disabled by
default because it makes Shady windows disappear whenever they lose focus,
and we want both the World and the interactive console to be visible at
the same time.  On Windows, `fullScreenMode=False` is what we do by default
anyway, but on Mac this has the disadvantage of making the menu bar visible.
We'll just have to put up with that for now. In non-interactive mode, on
Macs, `fullScreenMode=True` is the default.\n""")

	return cmdline
	
def AutoFinish( world, shell=False, prefer_ipython=True, plot='auto' ):
	"""
	A useful call at the end of a demo script, to navigate the various
	ways in which the script, and any `Shady.World` that was created in
	it, might be running (single- or dual-threaded by direct
	interpretation of the script; dual-threaded with the `World` running
	in the main thread and the script interpreted in a subsidiary thread
	via `python -m Shady`).
	
	Args:
	
	    world:
	        A `World` instance, ready to run.
	    
	    shell (bool):
	        Whether or not to spawn a threaded interactive shell while
	        the `World` is running.
	    
	    prefer_ipython (bool):
	        If a threaded shell is used, this indicates whether to try.
	        to import the third-party package `IPython` to improve the
	        interactive experience. If this is `False`, or if `IPython`
	        is not installed, then any interactive prompt spawned by
	        `shell=True` will be a plain-vanilla Python prompt.
	    
	    plot:
	        This argument can be:
	        
	        * a callable function with zero arguments: in this case it
	          is called when `world` finishes running; then it is
	          assumed that one or more `matplotlib` figures have been
	          generated by the call and that they should be kept alive
	          and responsive.
	        * a boolean specifying whether `matplotlib` figures already
	          exist that need to be kept alive and responsive when
	          `world` finishes running.
	        * `'auto'` (default):  If `world.debugTiming` is `True`,
	          then call `PlotTimings( world )` when `world` finishes
	          running.  If not, infer automatically whether there are
	          `matplotlib` figures.
	
	Returns:
	    `None`
	"""
	if plot == 'auto' and world.debugTiming:
		plot = lambda: PlotTimings( world )
	
	def PlottingPayload( wait=None ):
		keepFiguresAlive = plot
		if plot == 'auto':
			plt = DependencyManagement.LoadPyplot()
			keepFiguresAlive = True if plt and plt.get_fignums() else False
		if keepFiguresAlive:
			if callable( plot ): plot()
			FinishFigure( wait=wait )
	mainloop = world._thread_hijacker
	if shell:
		shell = ThreadedShell( on_close=world.Close, user_ns=-1, prefer_ipython=prefer_ipython )
		if shell:
			if not mainloop: mainloop = MainLoop()
			world.Run()
	if mainloop:
		if shell: mainloop.check = shell.isAlive
		if plot: mainloop.Queue( PlottingPayload, wait='block' )
		mainloop.Run()
	else:
		if plot and plot != 'auto': world.Run()  # wait for the world to finish if there's definitely going to be a plot to wait for
		PlottingPayload()
		if not world.threaded:
			world.Run()  # run the world if it's not already running in the background

def RunShadyScript( *argv, **kwargs ):
	"""
	If a script name is specified, run it.  If not, run an interactive prompt. In
	either case, interpret the commands in a new subsidiary thread---the main thread
	will be reserved.  Construction and running of one `Shady.World`, if performed
	in the script or from the prompt, will be diverted to the main thread.  This
	allows Shady applications to run in multi-threaded mode even on non-Windows
	operating systems, on which the graphical back-end insists on being in the main
	thread.
	
	With a script, the `console` option allows the script to run in demo mode,
	in which sections of the code can be run from an interactive prompt.
	
	This routine is used under the hood when you start Python with `-m Shady`.
	Here are some pairs of commands that produce equivalent results starting from
	outside and from inside Python::
	
		python -m Shady demo showcase
		--> RunShadyScript( 'showcase', console='IPython' )
	
		python -m Shady run showcase
		--> RunShadyScript( 'showcase', console=None )
		
		python -m Shady run showcase --console=Python
		--> RunShadyScript( 'showcase', console='Python' )
		
	Args:
	
		*argv
			positional arguments, just as you would use from a system command-line.
			If the first element `is sys.argv` then `sys.argv[1:]` will be used plus
			any subsequent `*argv` and `**kwargs` arguments.
			
		**kwargs
			optional keyword arguments, just as you would specify `--key=value`
			options from the command-line.  
		
	If you specify neither `argv` nor `kwargs`, then `sys.argv[1:]` will be used.
	Options are as follows:
		
		`--script` (or positional argument 0)
			The name of a Python script to run. If your script argument is not a
			valid (absolute or relative) path to an existing file, Shady will make
			a second attempt to find the named script inside the `examples`
			subdirectory of the `Shady` package itself (adding a `.py` extension
			if necessary).  If no script is specified, an interactive prompt will be
			opened instead.
	
		`--console`
			Values can be `'None'`, `'Python'` or `'IPython'`, specifying a preference
			for the type of interactive prompt that should be interleaved with script
			execution.  The default is `'IPython'` although Shady will fall back to
			`'Python'` if the third-party `IPython` package is not available.  `'None'`
			will only be respected if a script has been specified, and it causes the
			script to be run without any interaction from the console. 
	"""
	from .Rendering import World, CloseAllWorlds, WaitForAllWorlds, PackagePath
	from .Console import SHELL_THREAD, RunScript
	if argv and argv[ 0 ] is getattr( sys, 'argv', [] ):
		argv = list( argv[ 0 ][ 1: ] ) +  list( argv[ 1: ] )
	else: argv = list( argv ) if ( argv or kwargs ) else None
	for item in kwargs.items(): argv.append( '--%s=%r' % item ) # kwargs get translated to strings
	cmdline = CommandLine( argv )
	script = cmdline.Option( 'script', '', position=0, type=str ) # ...and back
	interaction = cmdline.Option( 'console', 'IPython', type=( bool, str ), strings=( 'None', 'Python', 'IPython' ) ) 
	skip = cmdline.Option( 'skipShadyInteractionUntilTheEnd', False, type=bool ) 
	if interaction == 0: interaction = 'None'
	if interaction == 1: interaction = 'IPython'
	if not script and interaction in [ 'None' ]: interaction = 'IPython'
	prefer_ipython = ( interaction in [ 'IPython' ] )
	interactive = ( interaction not in [ 'None' ] ) 
	if interactive and skip: interactive = 'final'
	createThread = interactive or not sys.platform.lower().startswith( 'win' )
	if threading.current_thread() is SHELL_THREAD: createThread = False
	import Shady
	user_ns = { 'Shady': Shady, '__name__' : '__main__' }
	user_ns.update( dict( os=os, sys=sys, time=time ) )
	if numpy: user_ns[ 'numpy' ] = user_ns[ 'np' ] = numpy
	on_close = [ CloseAllWorlds if interactive else WaitForAllWorlds ]
	try:
		if script: sys.argv[ 1: ] = cmdline.Delegate()
		else: cmdline.Finalize()
	
		if createThread:
			main = World._thread_hijacker = MainLoop()
			on_close.append( main.Stop )
		else:
			main = None
	
		if script:
			if not os.path.isabs( script ) and not os.path.isfile( script ):
				for fullPath in [ PackagePath( 'examples', script ), PackagePath( 'examples', script + '.py' ) ]:
					if os.path.isfile( fullPath ): script = fullPath; break
			thread = RunScript( script, on_close=on_close, user_ns=user_ns, prefer_ipython=prefer_ipython, threaded=createThread, color=True, interactive=interactive )
		else:
			thread = ThreadedShell( on_close=on_close, user_ns=user_ns, prefer_ipython=prefer_ipython, threaded=createThread )
		if main:
			if thread: main.check = thread.isAlive
			main.Run()
		if thread is not None:
			t0 = time.time()
			while thread.isAlive() and time.time() < t0 + 3.0:
				if '_SHADY_CONSOLE_EXCEPTION_INFO' in user_ns: break
				time.sleep( 0.010 )
		ei = user_ns.pop( '_SHADY_CONSOLE_EXCEPTION_INFO', None )
		if ei: reraise( *ei )
	except CommandLineError as exc:
		print( exc )

def ComplexPolygonBase( nsides, appendNaN=True, joined=False ):
	"""
	Return a 1-by-n `numpy.array` of complex numbers that describe the vertices
	of a polygon. 
	
	Args:
		nsides (int):
			number of sides (or vertices) of the polygon.
		appendNaN (bool):
			whether to append a NaN (interpreted as a break between polygons
			in the `Stimulus.points` property).
		joined (bool):
			whether to repeat the first vertex explicitly at the end. Only
			necessary if you want to draw unfilled (i.e. wireframe) closed
			polygons.
		
	Returns:
		a 1-by-n `numpy.array` of complex numbers, where `n` is `nsides`, plus
		1 if `appendNaN` is True, plus 1 if `joined` is True.
	
	Example::
		
		from Shady import World, ComplexPolygonBase, Real2DToComplex
		w = World(1000)
		s = w.Stimulus( drawMode=Shady.DRAWMODE.POLYGON, anchor=-1, color=[1,0,0] )
		shape = 50 * ComplexPolygonBase( 12 )
		locations = 150 * ComplexPolygonBase( 3, appendNaN=False ).T
		s.points = shape + locations
	
	See also:
		- `Real2DToComplex()`
		- `ComplexToReal2D()`
		
	"""
	circ = numpy.linspace( 0.0, 1.0, nsides + int( joined ), endpoint=joined )
	if appendNaN: circ = numpy.append( circ, numpy.nan )
	return numpy.exp( circ * numpy.pi * 2.0j )[ None, : ]

def Real2DToComplex( x, add_dims_left=0, add_dims_right='auto' ):
	"""
	Given an n-by-2 array of real-valued coordinates, return the coordinates
	as an array of complex numbers (default shape n-by-1, but depends on
	`add_dims_left` and `add_dims_right`).
	
	Alternatively, given *one* coordinate expressed as a 2-element numeric
	sequence (i.e. a list, tuple or 1-D numpy array of length 2), return a
	single complex number.
	
	Inverse of `ComplexToReal2D()`
	"""
	if len( x ) == 2 and isinstance( x[ 0 ], ( int, float ) ) and isinstance( x[ 1 ], ( int, float ) ):
		if add_dims_right == 'auto': add_dims_right = 0
		if add_dims_left == 0 and add_dims_right == 0: return x[ 0 ] + 1j * x[ 1 ]
		else: x = numpy.array( x )[ None, : ]
			
	if add_dims_right == 'auto': add_dims_right = 1
	x = numpy.dot( x, [ 1.0, 1.0j ] )
	x.shape = ( 1, ) * add_dims_left + ( x.size, ) + ( 1, ) * add_dims_right
	return x
	
def ComplexToReal2D( x ):
	"""
	Given a single complex number `x`, return `[ x.real, x.imag ]`. Or, by
	extension, given a single scalar real number `x`, return `[ float(x), 0.0 ]`. 
	
	Alternatively, if `x` is a sequence (i.e. a list, tuple or numpy array)
	of complex numbers, convert to an n-by-2 array of real-valued coordinates.
	
	Inverse of `Real2DToComplex()`
	"""
	if isinstance( x, ( int, float ) ): return [ float( x ), 0.0 ]
	elif isinstance( x, complex ): return [ x.real, x.imag ]
	return numpy.c_[ x.real.flat, x.imag.flat ]


class VideoRecording( object ):
	"""
	This class allows frames (in the form of `numpy` arrays) to be written
	to a video file.  It wraps the `VideoWriter` class from OpenCV. 
	
	It requires third-party packages `numpy` and `cv2` (the latter being part
	of `opencv-python`).
	
	Write frames with `.WriteFrame()`.  Remember to `.Close()` when finished.
	
	Example (capture video of one particular `Stimulus`):: 
		
		world = Shady.World( canvas=True, gamma=-1, noise=-0.1 )
		stim = world.Stimulus( sigfunc=1, siga=0.4, pp=0, cx=lambda t:t*100, atmosphere=world )
		
		world.fakeFrameRate = 60.0     # ensures accurate slower-than-real-time animation
		                               # (because .Capture() operations may be slow)
		movie = Shady.VideoRecording( 'example_movie', fps=world )
		world.OnClose( movie.Close )
		
		@stim.AnimationCallback
		def StimFrame( self, t ):
			movie.WriteFrame( self )   # we can pass a frame directly as a `numpy` array,
			                           # or we can pass a `Stimulus` or `World` instance
			                           # in which case its `.Capture()` method will be
			                           # called automatically
		world.Run()
		
	"""
	def __init__( self, filename, fps=60.0, codec='mp4v', container='.avi' ):
		"""
		Args:
			filename (str):
				stem, or name, or path, to the video file to be saved. If `filename`
				includes a file extension, the container format is inferred from that
				instead of from the `container` argument.
			
			fps (int, float, World):
				frames per second.  Can also use a `World` instance if that instance's
				`.fakeFrameRate` property has been set.
			
			codec (str):
				four characters that specify the FOURCC code of the codec to use.
				The default 'mp4v' is a reasonably safe cross-platform/out-of-the-box
				option, especially with the .avi container format. But, as with all things
				OpenCV, and indeed all things video-codec-related, your mileage may vary
				considerably. Note that 'mp4v' is a lossy codec.  For lossless compression
				(and hence perfectly accurate reconstruction of your stimuli) you may need
				to install a third-party codec---this seems to be quite a technical task
				so we can't go into detail here.
			
			container (str):
				file extension dictating the default video container format (used only if
				there is no file extension in `filename`).
		"""
		self.__file = None
		self.__codec = codec
		self.__frame = 0
		
		if hasattr( fps, 'fakeFrameRate' ): fps = fps.fakeFrameRate
		if not fps: fps = 60.0
		self.__fps = fps

		container = container.lstrip( '.' )
		if not container: container = 'avi'
		stem, xtn = os.path.splitext( filename )
		if not xtn.strip( '.' ): filename = stem + '.' + container
		self.filename = os.path.realpath( filename )
		

	
	@property
	def codec( self ): return self.__codec
	@codec.setter
	def codec( self, value ):
		if self.__file: raise AttributeError( 'cannot change the `.codec` attribute once recording has started' )
		else: self.__codec = value
		
	@property
	def fps( self ): return self.__fps
	@fps.setter
	def fps( self, value ):
		if self.__file: raise AttributeError( 'cannot change the `.fps` attribute once recording has started' )
		else: self.__fps = value
	
	@property
	def frame( self ): return self.__frame
		
	def WriteFrame( self, frame ):
		"""
		The `frame` argument can be a `numpy` array, height x width x channels,
		of uint8 pixel values. The number of channels should be either 3 (RGB) or
		4 (RGBA). The alpha channel, if any, will be ignored.
		
		Alternatively, `frame` can be a `Stimulus` or `World` instance, in which
		case its `.Capture()` method is called automatically.
		
		Note that, once the first frame is written, you should ensure that all subsequent
		frames have the same dimensions as the first.
		"""
		cv2 = DependencyManagement.Import( 'cv2', packageName='opencv-python', registerVersion=True )
		
		if hasattr( frame, 'Capture' ): frame = frame.Capture()
		if not self.__file:
			if isinstance( self.codec, str ):
				try: fourcc = cv2.VideoWriter_fourcc( *self.codec )
				except: fourcc = cv2.cv.CV_FOURCC( *self.codec )
			else:
				fourcc = self.codec
			self.__file = cv2.VideoWriter(
				self.filename,
				fourcc = fourcc,
				fps = self.fps,
				frameSize = ( frame.shape[ 1 ], frame.shape[ 0 ] ),
				isColor = True,
			)
			if not self.__file.isOpened(): raise IOError( 'failed to open video file %r' % self.filename )
		self.__file.write( frame[ :, :, 2::-1 ] )
		self.__frame += 1
	
	def Close( self ):
		if self.__file and self.__file.isOpened(): self.__file.release()
		self.__file = None
	
	def __del__( self ):
		self.Close()

