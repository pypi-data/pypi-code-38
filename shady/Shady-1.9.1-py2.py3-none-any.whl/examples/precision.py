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

#: Another test of the shader's linearization/dithering accuracy
"""
This demo tests the accuracy of the pipeline consisting of gamma-
correction followed by "noisy-bit" dithering  (Allard & Faubert 2008) as
implemented in our fragment shader.

Render a stimulus in which desired luminance climbs from 0.0 on the left
to 1.0 on the right, with a configurable number of steps. For each given
target luminance level, the shader's dithering algorithm renders either
the nearest realizable intensity level above the target or the nearest
one below---and this is done independently on each frame, in each color
channel, and in each row of the image.  This demo estimates accuracy by
automatically taking an instantaneous screen capture, then using Python
code to:

1. transform the resulting pixel values back through the screen
   nonlinearity, using the same gamma value that the shader had used
   to linearize the stimulus;
   
2. compute the quantization error between the desired target levels and
   the result, averaged across rows and color channels;
   
3. compute a lower bound on the precision implied by the observed
   quantization errors.  This is the size in bits, of a hypothetical
   discrete intensity scale in which `max(abs(error)))` corresponds to
   half a step size.

This demo requires third-party packages `numpy` and `matplotlib`. It
creates a `matplotlib` figure showing the results.

See also the `dithering` demo.
"""#.

if __name__ == '__main__':
	import Shady

	cmdline = Shady.WorldConstructorCommandLine( fullScreenMode=False, reportVersions=True )
	gammaValues = cmdline.Option( 'gamma', [ 1.0, 2.2 ], type=( int, float, tuple, list ), minlength=1, container=None, doc="A gamma value or a sequence of gamma values to use successively." )
	nRows       = cmdline.Option( 'nRows', 900, type=( int, None ), min=-1, container=None, doc="Number of image rows. Each row will have identical target values, but will be independently dithered. If `None`, fill the height of the screen." )
	nTargets    = cmdline.Option( 'nTargets', None, type=( int, None ), min=-1, container=None, doc="Number of target values. If `None`, use the highest power of 2 that will fit in the width of the screen." )
	waitFrames  = cmdline.Option( 'waitFrames', 5, type=( int ), min=1, container=None, doc="Number of frames to wait before capturing (will affect the random seed for the dithering noise)." )
	cmdline.Help().Finalize()
	numpy, matplotlib = Shady.Require( 'numpy', 'matplotlib' ) # die with an informative error if either is missing
	
	try: gammaValues[ 0 ]
	except: gammaValues = [ gammaValues ]

	"""
	Create a World:
	"""#:
	w = Shady.World( **cmdline.opts )

	"""
	Create a sequence of target values and render it as a texture: 
	"""#:
	if nRows in [ None, 0, -1 ]:
		nRows = w.height
	if nRows > w.height:
		nRows = w.height
		print( '\nnRows has been reduced to %d to fit in the World\n' % w.height )
	
	
	if nTargets in [ None, 0, -1 ]:
		nTargets = 2 ** int( numpy.log2( w.width ) )
		
	print( 'Rendering %d target luminance values (%g-bit)' % ( nTargets, numpy.log2( nTargets ) ) )
	targetValues = numpy.linspace( 0, 1, nTargets, endpoint=True )
	s = w.Stimulus( targetValues[ None, : ], height=nRows, atmosphere=w )

	"""
	Create an AnimationCallback that performs adjustment of the stimulus `.gamma`
	and `.ditheringDenominator`, and subsequent capture of the rendered pixel
	values, on successive frames.  This implementation takes advantage of Shady's
	built-in support for Python's "generator functions" (i.e. functions that use
	the `yield` keyword) as callbacks. The `yield` statements in the code delimit
	successive frames.
	"""#:

	@w.AnimationCallback
	def Sequence( self ):
		w.captured = {}
		for i in range( waitFrames ):
			yield  # come back here on the next frame
		for gamma in gammaValues:
			for ditheringDenominator in [ -self.dacMax, self.dacMax ]:
				s.Set( gamma=gamma, ditheringDenominator=ditheringDenominator )
				
				yield # allows one frame to be rendered, so that the new settings 
				      # can take effect before capturing
				
				# Capture and normalize
				rgb = s.Capture()[ :, :, :3 ] / self.dacMax
				# Undo the gamma-correction
				separateChannels = rgb[ :, :, 0 ], rgb[ :, :, 1 ], rgb[ :, :, 2 ]
				for x, channelGamma in zip( separateChannels, s.gamma ):
					x.flat = Shady.ScreenNonlinearity( x, channelGamma )
				# Transpose & reshape into a 2D array, (nRows*nChannels)-by-nTargets
				result = rgb.transpose( 0, 2, 1 ).reshape( [ nRows * 3, nTargets ] )
				# Store for later analysis
				w.captured[ ( gamma, ditheringDenominator ) ] = result
				
		self.Close()
		
	"""
	Define a couple of functions for analyzing the values that will end
	up in `w.captured`:
	"""#:
	def MeanErrors( output, targetValues ):
		"""
		Take the mean-across-rows of the captured, processed pixel array,
		and subtract the target values.
		"""
		return output.mean( axis=0 ) - targetValues
		
	def EquivalentPrecision( quantizationErrors, method='max' ):
		"""
		Compute the number of bits that would describe a uniformly-spaced scale
		in which the maximum absolute value of `quantizationErrors` (or possibly
		the mean or median absolute value, depending on `method`) corresponds to
		half a step size.
		"""
		return -numpy.log2( 2 * getattr( numpy, method )( numpy.abs( quantizationErrors ) ) )

	"""
	Now wait a second for the results to appear. You'll have to close the plot
	window manually in addition to exiting this prompt.
	"""#>
	def Plot():
		
		import matplotlib.pyplot as plt

		def LatexScientificNotation( x, fmt='%3.1e' ):
			import re
			if isinstance( x, ( float, int ) ): x = fmt % x
			return re.sub( r'[eE]([\+\-]?)0*([\.0123456789]+)$', r'\\times{}10^{\1\2}', x )
			
		axes = {}
		nPlots = len( gammaValues )
		layout = [ 1, nPlots ]
		transpose = nPlots > 2
		if transpose: layout = layout[ ::-1 ]
		for ( gamma, ditheringDenominator ), output in sorted( w.captured.items() ):
			if gamma not in axes:
				axes[ gamma ] = plt.subplot( layout[ 0 ], layout[ 1 ], len( axes ) + 1 )
			quantizationErrors = MeanErrors( output, targetValues )
			grandMeanError = quantizationErrors.mean()
			maxAbsError = numpy.abs( quantizationErrors ).max()
			precisionLowerBound = EquivalentPrecision( quantizationErrors, 'max' )
			print( 'gamma=%.1f, ditheringDenominator=%+g, grandMeanError=%+3.1e, maxAbsError=%3.1e, precisionLowerBound=%.2f bits' % (
				gamma, ditheringDenominator, grandMeanError, maxAbsError, precisionLowerBound
			) )
			label = r'Dithering %s: $\bar{\Delta{}v}=%s$, $|\Delta{}v|_{\max}=%s$, bits$\geq%.2f$' % (
				'ON' if ditheringDenominator > 0 else 'off',
				LatexScientificNotation( grandMeanError, '%+3.1e' ),
				LatexScientificNotation( maxAbsError, '%3.1e' ),
				precisionLowerBound,
			)
			plt.plot( targetValues, quantizationErrors, label=label )
			
		for iPlot, ( gamma, ax ) in enumerate( sorted( axes.items() ) ):
			if iPlot == 0 or transpose: ax.set_ylabel( 'Mean quantization error' )
			if iPlot == nPlots or not transpose: ax.set_xlabel( 'Target intensity level (normalized)' )
			ax.legend( loc='upper left' )
			yl = numpy.abs( ax.get_yticks() ).max()
			#yl += numpy.mean( numpy.diff( ax.get_yticks() ) )
			ax.set_ylim( [ -yl, yl ] )	
			ax.text( 0.02, 0.02, '$\gamma=%g$' % gamma, transform=ax.transAxes, size=20 )
			
		plt.subplots_adjust( 0.08, 0.1, 0.98, 0.98 )
		Shady.Utilities.FinishFigure( maximize=True )
	
	Shady.AutoFinish( w, plot=Plot )
