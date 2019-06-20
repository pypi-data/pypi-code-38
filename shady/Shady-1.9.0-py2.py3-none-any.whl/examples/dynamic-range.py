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

#: Noisy-bit dithering and bit-stealing under the microscope
"""
This is a demo of the `Loupe` utility function. It creates a
`Stimulus` that allows you to examine other stimuli empirically
with enhanced contrast, spatial magnification, and temporal
sub-sampling.  So it's good for verifying the content of 
very low-contrast stimuli and the behavior of the dynamic-range
enhancement tricks (bit-stealing or noisy-bit dithering) that
enable them.  This demo will allow you to explore `Loupe`
behavior with keyboard commands. It requires the third-party
packages `numpy` and `pillow`.

The concepts explored in this demo are explained in greater
detail in the topic documentation::

	>>> help( Shady.Documentation.PreciseControlOfLuminance )

or::
	
	In [1]: Shady.Documentation.PreciseControlOfLuminance?

"""#.
if __name__ == '__main__':
	"""
	Parse command-line options:
	"""#:
	import Shady
	cmdline = Shady.WorldConstructorCommandLine()
	gauge        = cmdline.Option( 'gauge', False,  type=bool,  container=None, doc="Whether or not to show a `FrameIntervalGauge`." )
	global_gamma = cmdline.Option( 'gamma',    -1,  type=( int, float, tuple, list ),  container=None, min=-1, minlength=3, maxlength=3, doc="Gamma-correction (when enabled). -1 means sRGB" )
	cmdline.Help().Finalize()

	"""
	We're going to need the `Shady.Text` plugin---be warned
	that that sometimes takes several seconds to import.
	Text-rendering also entails dependency on two third-party
	packages: `numpy` and `pillow`.
	"""#:
	import Shady.Text

	"""
	Create the World.  Add a FrameIntervalGauge if requested:
	"""#:
	world = Shady.World( **cmdline.opts )
	if gauge: f = Shady.FrameIntervalGauge( world )
	
	"""
	Create the Stimulus that a subject would actually see.
	We'll use a Gabor patch.
	"""#:
	ideal_size = 500
	size = int( min( ideal_size, world.width / 3.0 ) )
	shrink = size / float( ideal_size )
	margin = 100 * shrink

	gabor = world.Sine(  # convenience wrapper round `world.Stimulus`
		size = size,
		signalFrequency = 0.0125,
		plateauProportion = 0,
		position = world.Place( -1, 0 ) + [ margin, 0 ],
		anchor = [ -1, 0 ],
	)

	"""
	Create our diagnostic tool:
	"""#:
	enhanced = Shady.Loupe(
		target = gabor,
		update_period = 1.0,		
		scaling = 4,
		position = gabor.Place( +1, 0 ) + [ margin, 0 ],
		anchor = [ -1, 0 ],
	)

	"""
	Compute a bit-stealing LUT, or load a pre-computed one:
	"""#:
	lutArray = Shady.BitStealingLUT(
		maxDACDeparture = 2,
		Cmax = 3.0,
		nbits = 16,
		gamma = global_gamma,
		DACbits = world.dacBits,
		cache_dir = Shady.PackagePath( 'examples' ),
		# should pick up 'examples/BitStealingLUT_maxDACDeparture=2_Cmax=3.0_nbits=16_gamma=sRGB.npz'
        # unless you have requested a different --gamma, or your graphics card is not 8-bit
        # (in which case it will take a little extra time to calculate the LUT)
	) 
	lutObject = world.LookupTable( lutArray )  # keep this for later

	
	"""
	Accurate rendering breaks down as contrast gets low (close
	to detection threshold).  Exactly *how* it breaks down depends
	on whether the background luminance is an integer DAC value
	(say, 127) or not (say, 127.5 which is the true mid-point of
	an 8-bit DAC). We want to be able to visualize both cases.
	Let's create a function that allows us, regardless of whether
	we've got gamma correction turned on or off, to choose between
	a background luminance that maps to the nearest integer DAC
	value, and one that maps halfway between the two nearest integer
	DAC values.
	"""#:
	gabor.rounding = True
	approximateBackground = [ 0.5, 0.5, 0.5 ]
	targetDAC = []
	@world.AnimationCallback
	def WrangleBackground( t=None ):
		gamma = [ 1.0, 1.0, 1.0 ] if gabor.lut else gabor.gamma
		targetDAC[ : ] = [ int( world.dacMax * Shady.Linearize( val, gamma=g ) ) + ( 0 if gabor.rounding else 0.5 ) for val, g in zip( approximateBackground, gamma ) ]
		gabor.bg = [ Shady.ScreenNonlinearity( val / float( world.dacMax ), gamma=g ) for val, g in zip( targetDAC, gamma ) ]
	WrangleBackground()

	"""
	Create a dynamic text stimulus that reports all the relevant
	information about the Gabor's current linearization and
	dynamic-range enhancement settings:
	"""#:
	def Caption( t ):
		txt = '%g%% contrast\n' % ( gabor.contrast * 100 )
		if gabor.lut: txt += '%d-element look-up table' % gabor.lut.length
		else: txt += ( 'dithering off\n' if gabor.ditheringDenominator <= 0.0 else 'dithering on\n' ) + 'gamma = ' + str( list( gabor.gamma ) )
		if gabor.lut or gabor.rednoise: txt += '\nnoise = %g' % gabor.rednoise
		txt += '\nraw BG = %r' % targetDAC
		return txt
	msg = world.Stimulus( position=gabor.Place( -1, -1.2 ), anchor=[ -1, +1 ], text=Caption, text_align='left', text_size=35 * shrink  )

	"""
	Things only start to look interesting at lower contrasts,
	so let's start you there:
	"""#:
	gabor.contrast = 0.0625
	
	"""
	Register an event-handler that lets us play with the
	parameters:
	"""#:
	@world.EventHandler( slot=-1 )
	def KeyboardControl( self, event ):
		if event.type in [ 'key_release' ]:
			if event.key in [ 'right' ] and enhanced.update_period > 0.005: enhanced.update_period /= 2.0
			if event.key in [ 'left' ]  and enhanced.update_period < 30:    enhanced.update_period *= 2.0
			if event.key in [ 'down' ]: gabor.contrast /= 2.0
			if event.key in [ 'up' ]:   gabor.contrast *= 2.0
			if event.key in [ 'd' ]:    gabor.ditheringDenominator *= -1
			if event.key in [ 'l' ]:    gabor.lut = None if gabor.lut else lutObject
			if event.key in [ 'n' ]:    gabor.noise = 0 if any( gabor.noise ) else 1e-4
			if event.key in [ 'g' ]:    gabor.gamma = global_gamma if ( gabor.gamma[ 0 ] == 1.0 ) else 1.0
			if event.key in [ 'b' ]:    gabor.rounding = not gabor.rounding; WrangleBackground()
			enhanced.DeferredUpdate()
		if event.type in [ 'text' ]:
			if event.text in [ '-' ]:       enhanced.scaling /= 2.0
			if event.text in [ '+', '=' ]:  enhanced.scaling *= 2.0
			enhanced.DeferredUpdate()
			
	"""
	Print, and render, a reminder of the keyboard commands:
	"""#:
	instructions = """
  up / down  :  raise/lower contrast
left / right :  slower/faster capture rate
     D       :  toggle dithering
     G       :  toggle gamma-correction
     N       :  toggle additive noise
     L       :  toggle look-up table
     B       :  toggle integer/non-integer background DAC
   + / -     :  increase/decrease magnification
"""
	legend = world.Stimulus(
		text = instructions.strip( '\n' ),
		text_size = 20 * shrink,
		position = gabor.Place( 0, +1.2 ),
		anchor = ( 0, -1 ),
		z = +0.5,
	)
	print( instructions )
	
	"""
	Remember: the Loupe does not fake the effects of dithering
	and bit-stealing: it actually examines them empirically,
	enhancing them artificially so you can see them.  You can
	put whatever content you like into the target `Stimulus`
	(`gabor` in this case) and see the effects in the Loupe.
	"""#>
	Shady.AutoFinish( world )
