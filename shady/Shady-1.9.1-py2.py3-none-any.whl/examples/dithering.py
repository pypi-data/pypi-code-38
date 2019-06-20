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

#: Testing the accuracy of our "noisy-bit" dithering implementation
"""
This demo tests the accuracy of the "noisy-bit" dithering algorithm
(Allard & Faubert 2008) as implemented in our fragment shader.

A "uniform" canvas is rendered with each specified target DAC value
in turn.  After each is rendered, a function is called to capture
the screen and analyze its pixel content.  When the target DAC value
is an integer, the screen should be truly uniform and the error should
be zero.  When it is a non-integer value, only the integer values
immediately above and immediately below target should appear, and
the mean value across all pixels should be very close to the target.

See also the `precision` demo.
"""#.
if __name__ == '__main__':

	import Shady
	
	cmdline = Shady.WorldConstructorCommandLine()
	targetDACs = cmdline.Option( 'targetDAC', [0.5,1,254,254.5], type=( int, float, tuple, list ), min=0, container=None, doc='A DAC value or sequence of DAC values. If your graphics card is 8-bit, like most, then the values here should not exceed 255. Try integer and non-integer values.' )
	denom      = cmdline.Option( 'denom', 'auto', type=( int, float, str ), strings=[ 'auto' ], container=None, doc='You can explicitly override the default `.ditheringDenominator` here if you must. Otherwise it will be set appropriately for your graphics card (usually 255).' )
	gamma      = cmdline.Option( 'gamma', -1, type=( int, float ), min=-1, doc='Screen non-linearity parameter (-1 means "sRGB").' )
	cmdline.Help().Finalize()
	
	numpy = Shady.Require( 'numpy' ) # die with an informative error if this is missing

	cmdline.opts[ 'canvas' ] = True
	if denom != 'auto': cmdline.opts[ 'ditheringDenominator' ] = denom
	if isinstance( targetDACs, ( tuple, list ) ): targetDACs = list( targetDACs )
	else: targetDACs = [ targetDACs ]

	#print( '=' * 30 ); print( cmdline.opts ); print( '=' * 30 )

	def ScreenNonlinearity( targetDAC, gamma='sRGB', numType=float ):
		# same as Shady.ScreenNonLinearity, but can emulate what happens
		# when the calculations are performed at a different numeric precision
		# (e.g. numType=numpy.float32 would emulate the 32-bit float performance
		# of the shader)
		f = numType
		value = f( targetDAC ) / f( 255.0 )
		if gamma in [ 'sRGB' ] or gamma <= 0:
			value = ( ( ( value + f( 0.055 ) ) / f( 1.055 ) ) ** f( 2.4 ) ) if ( value > f( 0.04045 ) ) else ( value / f( 12.92 ) )
		else:
			value **= f( gamma )
		return value

	"""
	We'll define a Measure() function that starts by performing
	a .Capture() of the current world content, and then computes
	statistics on the resulting pixel values.
	"""#:
	def Measure( world, targetDAC ):
		a = world.Capture()
		hist = Shady.Histogram( a, DACmax=world.dacMax, plot=False )	
		print( '==== targetDAC = %r ==== ' % targetDAC )
		for k, counts in sorted( hist.items(), reverse=True ):
			nPixels = float( sum( counts ) )
			dacValues = numpy.arange( float( len( counts ) ) )
			avg = sum( dacValues * counts ) / nPixels
			print( '%s:  mean = %.5f' % ( k, avg ) )
			nonzero = [ ( dacValue, count ) for dacValue, count in zip( dacValues, counts ) if count ]
			if len( nonzero ) <= 5:
				for dacValue, count in nonzero: print( '   %3d: %.4f' % ( dacValue, count / nPixels  ) )
			else:
				print( '%d unique pixel values' % len( nonzero ) )
		error = ( a[ :, :, :3 ].mean() - targetDAC )
		if error:
			percentageStr = ' (%+3g %% of target)' % ( 100.0 * error / float( targetDAC ) ) if targetDAC else ''
			normalizedStepSizeImpliedByError = 2.0 * abs( error ) / ( world.dacMax + 1.0 )
			print( 'overall error = %+3g DAC units%s' % ( error, percentageStr ) )
			print( 'equivalent precision = %.2f bits\n' % -numpy.log2( normalizedStepSizeImpliedByError ) )
		else:
			print( 'overall error = 0\n' )

	""#.
	if 0:
		# TODO: this implementation is easier to understand, but it needs
		#       threading---either via `python -m Shady`,
		#       or (if the OS permits) natively with --threaded=True
		"""
		Render a "uniform" canvas with each specified target DAC value in
		turn.  After rendering each, call Measure()
		"""#:
		w = Shady.World( **cmdline.opts )
		for targetDAC in targetDACs:
			w.backgroundColor = ScreenNonlinearity( targetDAC, gamma=gamma, numType=numpy.float32 )
			w.Wait() # this will hang forever if we're not threaded
			Measure( w, targetDAC )
		w.Close()
		""#>
	elif 0:
		# TODO: this implementation is more robust, more suitable for a releasable
		#       example script, but the double-Defer is a bit opaque
		"""
		Render a "uniform" canvas with each specified target DAC value in
		turn.  After rendering each, call Measure()
		"""#:
		w = Shady.World( **cmdline.opts )
		@w.AnimationCallback
		def Animate( self, t ):
			if not targetDACs: return self.Close()
			targetDAC = targetDACs.pop( 0 )
			self.backgroundColor = ScreenNonlinearity( targetDAC, gamma=gamma, numType=numpy.float32 )
			self.Defer( self.Defer, Measure, world=self, targetDAC=targetDAC )
			# Defer()red actions get carried out immediately after this animation callback, before
			# the effect of the new .backgroundColor even gets rendered.  So we actually need to
			# double-Defer(), i.e. Defer() a call to Defer() which will schedule the Measure() function.
		""#>
	else:
		# TODO: this implementation is also robust, and so also suitable for a
		#       releasable example script, but the use of a generator function
		#       will inevitably be obscure to many
		"""
		Render a "uniform" canvas with each specified target DAC value in
		turn. After rendering each, call Measure().
		
		We're going to use a slightly obscure trick to ensure correct
		scheduling: we'll register a Python "generator function" as the
		animation callback, instead of a regular function. A generator
		function is any function with the `yield` keyword in it.
		
		Unusually for an animation callback, there's no `t` argument.
		This is because the function will actually only be called once
		(on the first frame after it is registered) rather than repeatedly
		on every frame. What then happens is that whenever we hit a
		`yield` statement, we pop out of the function back into Shady's
		main loop. And when the next frame comes around, we pop back in
		again to resume the function where we left off. (If we ever needed
		to know the time inside the generator code, it's always available
		as `self.t` anyway.)
		"""#:
		w = Shady.World( **cmdline.opts )
		@w.AnimationCallback
		def Animate( self ):
			for targetDAC in targetDACs:
				self.backgroundColor = ScreenNonlinearity( targetDAC, gamma=gamma, numType=numpy.float32 )
				yield # allow one frame for the `.backgroundColor` setting to take effect before we...
				Measure( w, targetDAC )
			self.Close()
	
		""#>
		Shady.AutoFinish( w )
