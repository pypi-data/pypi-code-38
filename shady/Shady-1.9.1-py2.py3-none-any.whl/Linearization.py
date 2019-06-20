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
This module contains several utility functions related
to linearization.

Some of these (`ScreenNonlinearity`, `Linearize`, `ApplyLUT`)
are only useful in special circumstances where we want to re-create
"offline" what the shader is doing for us on every frame.

Others (`LoadLUT`, `SaveLUT`) are for general management of
look-up table arrays.

Others (`BitStealingLUT`, `ReportBitStealingStats`) are useful
for creating and examining a specific type of look-up table
that employs a bit-stealing technique (after Tyler 1997).

Note that everything exported from this module is also available in
the top-level `Shady.*` namespace.
"""

__all__ = [
	'ScreenNonlinearity',
	'Linearize',
	
	'LoadLUT',
	'SaveLUT',
	'ApplyLUT',
	
	'BitStealingLUT',
	'ReportBitStealingStats',
]

import os
import sys
import math

from . import Dependencies; from .Dependencies import numpy, Image

def ScreenNonlinearity( x, gamma='sRGB' ):
	"""
	Maps normalized DAC values `x` (in the domain 0 to 1, which
	corresponds to DAC values 0 to 255 if we assume standard
	8-bit DACs) to ideal luminance `Y` (in the range 0 to 1),
	given the screen non-linearity parameter `gamma`.
	
	Generally, `gamma` is numeric and strictly positive, in which
	case the relationship is `Y = x ** gamma`.  A special case is
	`gamma='sRGB'`, which is also used if you pass a `gamma` value
	of 0 or less: this uses a slightly different piecewise equation,
	very close to the `gamma=2.2` curve (even though the exponent
	used in it is actually 2.4).
	
	Inverse of `Linearize()`
	"""
	func, arg = ScreenNonlinearity, x
	if numpy and numpy.asarray( gamma ).size > 1:
		gammaArray = numpy.asarray( gamma )
		argArray = numpy.asarray( arg )
		if argArray.ndim > 0 and gammaArray.size == argArray.shape[ -1 ]:
			axis = argArray.ndim - 1
			def split( a, axis=-1 ): return numpy.split( a, range( a.shape[ axis ] ), axis=axis )[ 1: ]
			return numpy.concatenate( [
				func( argSlice, gammaValue ) for argSlice, gammaValue in zip( split( argArray, axis=axis ), gammaArray.flat )
			], axis=axis )
		else:
			channels = [ numpy.asarray( func( arg, each_gamma ) ) for each_gamma in gammaArray.flat ]
			for channel in channels: channel.shape = tuple( channel.shape ) + ( 1, )
			return numpy.concatenate( channels, axis=channels[ 0 ].ndim - 1 )
			
	cls = float if isinstance( arg, ( int, float ) ) else None
	if numpy: value = numpy.array( arg, dtype='float64', copy=True )
	elif isinstance( arg, ( tuple, list ) ): return [ func( element, gamma=gamma ) for element in arg ]
	else: value = float( arg )
	
	if gamma in [ 'sRGB' ] or gamma <= 0:
		if numpy:
			nonlinear = value.flat > 0.04045
			value.flat[ ~nonlinear ] /= 12.92
			value.flat[ nonlinear ]  += 0.055
			value.flat[ nonlinear ]  /= 1.055
			value.flat[ nonlinear ] **= 2.4
		else:
			value = ( ( ( value + 0.055 ) / 1.055 ) ** 2.4 ) if ( value > 0.04045 ) else ( value / 12.92 )
	else:
		value **= gamma
	return cls( value ) if cls else value

def Linearize( Y, gamma='sRGB' ):
	"""
	Maps ideal luminance `Y` (in the domain 0 to 1) to
	normalized DAC values `x` (in the range 0 to 1, which
	corresponds to DAC values 0 to 255 if we assume standard
	8-bit DACs) given the screen non-linearity parameter `gamma`.
	
	Generally, `gamma` is numeric and strictly positive, in which
	case the relationship is `x = Y ** (1/gamma)`.  A special case
	is `gamma='sRGB'`, which is also used if you pass a `gamma`
	value of 0 or less: this uses a slightly different piecewise
	equation, very close to the `gamma=2.2` curve (even though the
	exponent used in it is actually 2.4).
	
	This allows us to emulate, on the CPU and in Python, the
	linearization operation performed automatically by the GPU in
	the fragment shader on every frame according to the value of
	of the `Stimulus.gamma` property.
	
	Inverse of `ScreenNonlinearity()`
	"""
	func, arg = Linearize, Y
	if numpy and numpy.asarray( gamma ).size > 1:
		gammaArray = numpy.asarray( gamma )
		argArray = numpy.asarray( arg )
		if argArray.ndim > 0 and gammaArray.size == argArray.shape[ -1 ]:
			axis = argArray.ndim - 1
			def split( a, axis=-1 ): return numpy.split( a, range( a.shape[ axis ] ), axis=axis )[ 1: ]
			return numpy.concatenate( [
				func( argSlice, gammaValue ) for argSlice, gammaValue in zip( split( argArray, axis=axis ), gammaArray.flat )
			], axis=axis )
		else:
			channels = [ numpy.asarray( func( arg, each_gamma ) ) for each_gamma in gammaArray.flat ]
			for channel in channels: channel.shape = tuple( channel.shape ) + ( 1, )
			return numpy.concatenate( channels, axis=channels[ 0 ].ndim - 1 )
			
	cls = float if isinstance( arg, ( int, float ) ) else None
	if numpy: value = numpy.array( arg, dtype='float64', copy=True )
	elif isinstance( arg, ( tuple, list ) ): return [ func( element, gamma=gamma ) for element in arg ]
	else: value = float( arg )
	
	if gamma is 'sRGB' or gamma <= 0:  # NB: looks very similar to a gamma of 2.2, even though the exponent it uses is 2.4
		if numpy:
			nonlinear = value.flat > 0.04045 / 12.92
			value.flat[ nonlinear ] **= 1.0 / 2.4
			value.flat[ nonlinear ]  *= 1.055
			value.flat[ nonlinear ]  -= 0.055
			value.flat[ ~nonlinear ] *= 12.92
		else:
			value = ( value ** ( 1.0 / 2.4 ) * 1.055 - 0.055 ) if ( value > 0.04045 / 12.92 ) else ( value * 12.92 )
	else:
		value **= 1.0 / gamma
	return cls( value ) if cls else value

def LoadLUT( source, DACbits=8 ):
	"""
	Load or prepare a look-up table array.
	
	Args:
		source (str, numpy.ndarray):
			Usually this is a string denoting a filename.  The file may
			be in numpy format - either a `.npy` file in which the the
			lookup-table has been written with `numpy.save`, or a `.npz`
			file into which the look-up table array has been saved with
			`numpy.savez` as either the sole variable or a variable called
			`lut`.   If the third-party `pillow` package is installed, the
			file may alternatively be a `.png` image file in which look-up
			table entries have been saved as R,G,B pixel values in column-
			first order.
			
			The `source` may also be a `numpy.ndarray` already.
						
		DACbits (int):
			This is the number of bits per DAC in the graphics card for
			which the look-up table is intended. In this function it is
			used to verify that the lookup-table entries are in range
			and to cast the output as the appropriate numeric data-type.
			
	Returns:
		Whether `source` is a filename or an array already, in either case,
		this function ensures that the returned result is a 3-dimensional
		`numpy` array, of the appropriate integer type, with extent 3 (RGB)
		or 4 (RGBA) in its third dimension.
		
	See also:
		- `SaveLUT()`
		
	"""
	if not numpy: raise ImportError( 'cannot manipulate lookup-table values unless you install the `numpy` package' )
	if isinstance( source, str ):
		file_name = source
		if file_name.lower().endswith( '.npy' ):
			source = numpy.load( file_name )
		elif file_name.lower().endswith( '.npz' ):
			vars = numpy.load( file_name )
			if len( vars.keys() ) == 1: source = vars[ list( vars.keys() )[ 0 ] ]
			else: source = vars[ 'lut' ]
			try: DACbits = vars[ 'DACbits' ]
			except: pass
		else:
			if not Image: raise ImportError( 'cannot load LUT from image file unless you install the `PIL` or `pillow` package' )
			source = Image.open( file_name )
			
	values = numpy.array( source, copy=False )
	if values.ndim == 3: values = values.transpose( [ 1, 0, 2 ] ).reshape( [ values.shape[ 0 ] * values.shape[ 1 ], values.shape[ 2 ] ] )
	if values.ndim == 2: values = values[ :, None, : ]
	if values.ndim != 3: raise ValueError( 'LUT array must be 2- or 3- dimensional' )
	if values.shape[ -1 ] not in [ 3, 4 ]: raise ValueError( 'LUT array must have extent 3 or 4 in its highest dimension (RGB or RGBA)' )
	if values.min() < 0 or not 2 <= values.max() <= 2 ** DACbits - 1: raise ValueError( 'LUT values must be in range [0, %d]' % ( 2 ** DACbits - 1 ) )
	dtype = 'uint8' if DACbits <= 8 else 'uint16' if DACbits <= 16 else 'uint32'
	values = values.astype( dtype, copy=False )
	return values
	

def SaveLUT( filename, lut, luminance=(), DACbits=8 ):
	"""
	Save a look-up table array, and optionally also the
	corresponding sequence of luminance values, in a file.
	
	Args:
		filename (str):
			name of the file to save. Determines the file
			format, and should end in `.npy`, `.npz` or `.png`
			
		lut (numpy.array):
			look-up table array, `n`-by-3 or `n`-by-1-by-3 as
			per the output of `LoadLUT()` or `BitStealingLUT()`,
			where `n` is the number of entries. If the format
			is `.npz` the array will be saved under the
			variable name `lut`.
		
		luminance (numpy.array, list):
			sequence of `n` ideal luminance values (i.e.
			luminance values in the range 0 to 1) corresponding
			to each of the look-up table entries. Only saved
			(under the variable name `luminance`) if the file
			format is `.npz`
			
		DACbits (int):
			This is the number of bits per DAC in the graphics
			card for which the look-up table is intended. In this
			function it is used to verify that the lookup-table
			entries are in range and to cast the output as the
			appropriate numeric data-type.
		
	Returns:
		a tuple consisting of:
		
		- the filename
		- the look-up table array in standardized format
		- the sequence of luminance values
	
	
	See also:
		- `LoadLUT()`
		
	"""
	lut = LoadLUT( lut, DACbits=DACbits ) # standardizes array
	if filename:
		xtn = os.path.splitext( filename )[ -1 ].lower()
		if not xtn: xtn = '.npz'; filename += xtn
		if   xtn == '.npz': numpy.savez_compressed( filename, lut=lut, luminance=luminance, DACbits=DACbits )
		elif xtn == '.npy': numpy.save( filename, lut ) # only room for one variable in this format, so `luminance` is discarded
		elif xtn == '.png':
			img = lut
			if img.ndim not in [ 3, 4 ]:
				img = img.reshape( [ img.size // img.shape[ -1 ], 1, img.shape[ -1 ] ] )
			Image.fromarray( img ).save( filename )
		else: raise ValueError( 'file format must be .npz, .npy or .png' )
		
	return filename, lut, luminance


def RGB_to_YLCHab( inputColor, gamma='sRGB', DACbits=8 ) :
	"""
	Transform a triplet of integer DAC values, or each row of a
	three-column numpy array/matrix, according to::

		[R,G,B] -> [Y, L, C_ab, H_ab ]
	
	`Y` is luminance from the XYZ space. The others are from the
	LCH_ab space::
	
		L     : lightness (not luminance)
		C_ab  : chroma (i.e. saturation) in the {a,b} plane, in percent
		H_ab  : hue angle in the {a,b} plane, in degrees:  0 <= H_ab < 360
	
	"""
	if hasattr( inputColor, '__len__' ): # deal with various numeric sequence types without actually invoking the symbol `numpy`
		original = inputColor
		if hasattr( inputColor, 'A' ): inputColor = inputColor.A     # numpy matrix to numpy array
		if hasattr( inputColor[ 0 ], '__len__' ):   # deal with numpy array
			out = [ RGB_to_YLCHab( c, gamma=gamma, DACbits=DACbits ) for c in inputColor ]
			if numpy: return numpy.array( out )
			else: return type( original )( out )
				
	if hasattr( inputColor, 'flat' ): inputColor = inputColor.flat  # make slice of numpy array accessible as ordinary sequence

	R, G, B = inputColor
	
	# Part I: convert to XYZ
	
	DACmax = 2.0 ** DACbits - 1.0
	R, G, B = [ ScreenNonlinearity( value / DACmax, gamma=gamma ) * 100.0 for value in [ R, G, B ] ]
	X = R * 0.4124 + G * 0.3576 + B * 0.1805 # These matrix values are presumably sRGB-specific
	Y = R * 0.2126 + G * 0.7152 + B * 0.0722 #
	Z = R * 0.0193 + G * 0.1192 + B * 0.9505 #

	luminance = Y         # Z is an idealized S-cone response, and X is an imaginary color to keep the whole thing non-negative
	

	# Part II: convert XYZ to Lab
	X /= 95.047       # ref_X =  95.047  Observer= 2 degrees, Illuminant= D65
	Y /= 100.0        # ref_Y = 100.000
	Z /= 108.883      # ref_Z = 108.883

	def transformXYZ( value ):
		if value > 0.008856:
			value **= 1.0 / 3.0
		else:
			value = 7.787 * value + 16.0 / 116.0
		return value
		
	X, Y, Z = [ transformXYZ( value ) for value in [ X, Y, Z ] ]

	L = ( 116.0 * Y ) - 16.0    # NB: stands for lightness, not luminance
	a = 500.0 * ( X - Y )
	b = 200.0 * ( Y - Z )

	# Part III: convert Lab to cylindrical representation LCHab
	Cab = ( a * a + b * b ) ** 0.5                  # Chroma (saturation) in ab plane
	Hab = math.atan2( b, a ) * 180.0 / math.pi      # Hue angle in ab plane
	Hab %= 360.0
	
	return [ luminance, L, Cab, Hab ]

def BitStealingLUT( maxDACDeparture=2, Cmax=3.0, nbits=16, gamma='sRGB', cache_dir=None, DACbits=8 ):
	"""
	Create an RGB look-up table that (a) linearizes pixel intensity values
	according to the specified `gamma` profile, and (b) increases dynamic
	range using a "bit-stealing" approach (after Tyler 1997).
	
	Args:
	    maxDACDeparture (int):
	        Red, green and blue DAC values will be considered only up
	        to +/- this value relative to the `R==G==B` line
	
	    nbits (int):
	        The look-up table will have `2 ** nbits` entries. It doesn't
	        hurt to specify a high number here, like 16---however, note
	        that, depending on the values of `maxDACDeparture` and `Cmax`
	        you may not get that many distinct or evenly-spaced luminance
	        levels. The actual effective precision can be investigated
	        using `ReportBitStealingStats()`
	
	    Cmax (float):
	        `[R,G,B]` triples will not be considered if the
	        corresponding chroma, in percent (i.e. the third
	        column of `RGB_to_YLCHab()` output) exceeds this.
	        
	    gamma (float):
	        screen non-linearity parameter (see `ScreenNonlinearity()`)
	    
	    cache_dir (str, None):
	        optional directory in which to look for a cached copy of
	        the resulting LUT (or save one, after creation, if the
	        appropriately-named file was not found there).
	        
		DACbits (int):
			The number of bits per digital-analog converter in the
			graphics card for which the look-up table is intended.
			LUT values will be scaled accordingly.
	
	Returns:
		`numpy` array  of shape `[2**nbits, 1, 3]` with the appropriate
		integer type (usually `uint8`), containing integer RGB triplets.
	
	"""
	verbose_caching = True
	cache_file = None
	maxDACDeparture = int( maxDACDeparture )
	Cmax = float( Cmax )
	nbits = int( nbits )
	DACbits = int( DACbits )
	if cache_dir:
		if isinstance( gamma, ( int, float ) ) and gamma <= 0.0: gamma = 'sRGB'
		filename = 'BitStealingLUT_maxDACDeparture=%s_Cmax=%s_nbits=%s_gamma=%s' % ( maxDACDeparture, Cmax, nbits, gamma )
		if DACbits != 8: filename += '_DACbits=%d' % DACbits
		xtns = '.npz .npy .png'.split()
		cache_files = [ os.path.join( cache_dir, filename + xtn ) for xtn in xtns ]
		existing_cache_files = [ x for x in cache_files if os.path.isfile( x ) ]
		if existing_cache_files: cache_file = existing_cache_files[ 0 ]
		else: cache_file = cache_files[ 0 ]
		if existing_cache_files:
			if verbose_caching:
				sys.stderr.write( 'loading LUT from cache file %s\n' % cache_file )
				try: sys.stderr.flush()
				except: pass
			return LoadLUT( cache_file, DACbits=DACbits )
	
	a = numpy.arange( 2 ** DACbits )
	a.shape = [ 2 ** DACbits, 1 ]
	RGB = numpy.tile( a, ( 1, 3 ) )
	arrays = []
	deltas = range( -abs( maxDACDeparture ), abs( maxDACDeparture ) + 1 )
	for rdelta in deltas:
		for gdelta in deltas:
			for bdelta in deltas:
				arrays.append( RGB + [ [ rdelta, gdelta, bdelta ] ] )
	RGB = numpy.concatenate( arrays, axis=0 )
	RGB = RGB[ numpy.logical_and( RGB >= 0, RGB <= 2 ** DACbits - 1 ).all( axis=1 ), : ]
	
	# row-wise sort and keep unique rows
	indices = numpy.lexsort( RGB.T[ : : -1 ] )
	RGB = RGB[ indices, : ]
	indices = numpy.arange( len( RGB ) )
	unique = numpy.nonzero( ( RGB[ indices, : ] != RGB[ indices - 1, : ] ).any( axis=1 ) )[ 0 ]
	RGB = RGB[ unique, : ]
	dtype = 'uint8' if DACbits <= 8 else 'uint16' if DACbits <= 16 else 'uint32'
	RGB = numpy.asarray( RGB, dtype=dtype )
	
	YLCHab = RGB_to_YLCHab( RGB, gamma=gamma, DACbits=DACbits )
	
	# re-sort
	indices = numpy.lexsort( YLCHab.T[ : : -1 ] )
	YLCHab = YLCHab[ indices, : ]
	RGB = RGB[ indices, : ]
	
	if Cmax is not None:
		sel = YLCHab[ :, 2 ] <= Cmax
		RGB = RGB[ sel, : ]
		YLCHab = YLCHab[ sel, : ]
		
	lut = numpy.zeros( [ 2 ** nbits, 3 ], dtype=dtype )
	luminance = numpy.zeros( [ 2 ** nbits ], dtype=numpy.float64 )
	lumIndex = 0
	factor = 100.0 / ( 2 ** nbits - 1 )
	for addr in range( 2 ** nbits ):
		ideal = addr * factor
		while lumIndex + 1 < len( YLCHab ) and abs( ideal - YLCHab[ lumIndex + 1, 0 ] ) < abs( ideal - YLCHab[ lumIndex, 0 ] ): lumIndex += 1
		lut[ addr, : ].flat = RGB[ lumIndex, : ]
		luminance[ addr ] = YLCHab[ lumIndex, 0 ]
		
	if verbose_caching and cache_file:
		sys.stderr.write( 'saving LUT to cache file %s' % cache_file )
		try: sys.stderr.flush()
		except: pass
	
	if cache_file: SaveLUT( cache_file, lut, luminance, DACbits=DACbits )
	return lut

def ReportBitStealingStats( lut=None, image=None, gamma='sRGB', DACbits=8 ):
	"""
	Prints to the console certain statistics about the look-up table `lut`,
	if supplied, and optionally also any given `image` that has been
	through the look-up process (i.e. an output of `ApplyLUT()`).
	
	Make sure that the `gamma` and `DACbits` arguments match the values
	that were used for creating `lut`.
	"""
	
	print( '' )
	
	if image is not None:
		print( '  Red DAC values in image: %s' % str( list( set( image[ :, :, 0 ].flat ) ) ) )
		print( 'Green DAC values in image: %s' % str( list( set( image[ :, :, 1 ].flat ) ) ) )
		print( ' Blue DAC values in image: %s' % str( list( set( image[ :, :, 2 ].flat ) ) ) )
		print( 'Max std between image colour channels = %g' % numpy.std( image[ :, :, :3 ], axis=2 ).max() )
		print( '' )

	if lut is not None:
		lut = LoadLUT( lut, DACbits=DACbits )
		YLCHab = RGB_to_YLCHab( lut, gamma=gamma, DACbits=DACbits )
		YLCHab = YLCHab.reshape( [ YLCHab.size // YLCHab.shape[ -1 ], YLCHab.shape[ -1 ] ] )
		nLevels = YLCHab.shape[ 0 ]
		luminance_0_to_100 = YLCHab[ :, 0 ]
		chroma_percent = YLCHab[ :, 2 ]
		print( 'Number of LUT entries is %d' % lut.shape[ 0 ] )
		nsteps = ( numpy.diff( luminance_0_to_100 ) != 0 ).sum()
		print( 'Number of non-zero steps in LUT is %d (%.f%%, dynamic range <= %.1f bits)' % ( nsteps, nsteps * 100.0 / ( nLevels - 1 ), numpy.log( nsteps + 1 ) / numpy.log( 2 ) ) )
		print( 'Maximum chroma in LUT is %.4f%%' % chroma_percent.max() )
		step = numpy.diff( luminance_0_to_100 ).max()
		print( 'Maximum luminance step size over whole LUT is %.4f%% (dynamic range >= %.1f bits)' % ( step, numpy.log( 100.0 / step ) / numpy.log( 2 ) )  )
		sel = numpy.logical_and( luminance_0_to_100 >= 45, luminance_0_to_100 < 55 )
		step = numpy.diff( luminance_0_to_100[ sel ] ).max()
		print( 'Maximum luminance step size in central 10%% of LUT is %.4f%% (dynamic range >= %.1f bits spanning central range)' % ( step, numpy.log( 10.0 / step ) / numpy.log( 2 ) )  )
		print( '' )

def ApplyLUT( image, lut, noiseAmplitude=0, DACbits=8 ):
	"""
	Translate an array of `image` pixel values via a look-up table `lut`.
	
	This allows us to emulate, on the CPU in Python, the look-up operation
	performed automatically by the GPU in the shader on every frame if a
	look-up table has been configured via the `Stimulus.lut` property.
	
	Args:
		image (numpy.array):
			Source pixel values. If the array data type is floating-point,
			pixel values are assumed to refer to ideal luminances in the
			range 0 to 1, and are clipped to this range before scaling and
			rounding according to the size of the `lut`. If the array is
			of some integer type, the values are assumed to be direct
			indices into the look-up table.
			
			Note that, if the image has more than one color channel (i.e.
			it has a third dimension with extent > 1) then only the first
			channel (red) will be used.
			
		lut (numpy.array):
			Look-up table array, e.g. as output by `LoadLUT()` or
			`BitStealingLUT()`.
		
		noiseAmplitude (float):
			specifies the amplitude of an optional random signal that can
			be added to `image` pixel values before lookup. A negative
			value indicates a uniform distribution (in the range
			`[noiseAmplitude, -noiseAmplitude]`) whereas a positive value
			is interpreted as the standard deviation of a Gaussian noise
			distribution.
			
		DACbits (int):
			The number of bits per digital-analog converter in the
			graphics card for which the look-up table is intended.
			Floating-point image pixel values will be scaled accordingly.
			
	Returns:
		An array of integer DAC values post-lookup. First two dimensions
		match those of the input `image`. Extent in the third dimension
		will match that of `lut`.	
	"""
	dtype = 'uint8' if DACbits <= 8 else 'uint16' if DACbits <= 16 else 'uint32'
	lut = numpy.asarray( lut, dtype=dtype )
	lut = lut.view()
	#while lut.ndim < 2: lut.shape = tuple( lut.shape ) + ( 1, )
	if max( lut.shape ) == lut.size:
		lut.shape = ( lut.size, 1 )
		lut = numpy.tile( lut, ( 1, 3 ) )
	targetShape = [ lut.size // lut.shape[ -1 ], 1, lut.shape[ -1 ] ]
	if list( lut.shape ) != targetShape:
		lut = lut.copy().reshape( targetShape )
	
	image = numpy.asarray( image )
	if image.dtype == numpy.uint8: image = image / 255.0
	elif image.dtype not in [ numpy.float32, numpy.float64 ]: image = image / ( 2.0 ** DACbits - 1.0 )
	if image.ndim == 3: image = image[ :, :, 0 ]   #  image = numpy.mean( image[ :, :, :3 ], axis=2 )
	if image.ndim > 2: raise ValueError( "image can have at most 3 dimensions" )
	#while image.ndim < 2: image.shape = tuple( image.shape ) + ( 1, )
	if noiseAmplitude > 0: image = image + numpy.random.normal( loc=0, scale=noiseAmplitude, size=image.shape )
	if noiseAmplitude < 0: image = image + numpy.random.uniform( low=noiseAmplitude, high=-noiseAmplitude, size=image.shape )
	indMax = lut.shape[ 0 ] - 1
	if image.dtype in [ numpy.float32, numpy.float64 ]: image = numpy.array( image * indMax, dtype=int )
	else: image = numpy.array( image, dtype=int )
	image = image.clip( 0, indMax )
	out = lut[ image, : ]
	out.shape = tuple( image.shape ) + ( lut.shape[ -1 ], )
	#out.shape = ( image.shape[ 0 ], image.shape[ 1 ], 3 )
	return out
