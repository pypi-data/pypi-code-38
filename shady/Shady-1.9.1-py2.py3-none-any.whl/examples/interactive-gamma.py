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

#: Demonstrates an interactive perceptual-linearization tool
"""
This script demonstrates the `FindGamma()` utility function.
It creates a `LinearizationTestPattern()` stimulus, displays it,
and then installs an `EventHandler` that allows interactive gamma
adjustment with the mouse or touchscreen.

This demo requires the third-party package `numpy`, used in the
generation of the `LinearizationTestPattern()`.
"""#.
if __name__ == '__main__':

	import Shady

	"""
	Parse command-line options:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( canvas=True )
	gamma = cmdline.Option( 'gamma',  1.0, type=( int, float, tuple, list ), doc='Start value(s) for exponent `.gamma` that should be corrected-for.' )
	xBlue = cmdline.Option( 'xblue', True, type=bool, container=None, doc='Whether or not to adjust blue gamma separately, relative to the others, with horizontal movement.' )
	text  = cmdline.Option( 'text', True, type=bool, container=None, doc='Whether or show the gamma values as text on screen.' )
	cmdline.Help().Finalize()
	Shady.Require( 'numpy' ) # die with an informative error if this is missing

	"""
	Create a `World`, along with a `Stimulus` that might benefit
	from linearization:
	"""#:
	world = Shady.World( **cmdline.opts )
	gabor = world.Sine(
		size = min( world.width / 2, world.height ) * 0.75,
		x = -world.width / 4,
		plateauProportion = 0,
		signalFrequency = 0.01,   # 100 pixels per cycle
		cx = lambda t: t * 100,   # 100 pixels per second
		contrast = Shady.Oscillator( 0.2 ) * 0.5 + 0.5,
	)
	# NB: The `w.Sine()` method is a wrapper around `w.Stimulus`.
	#     Among other settings, it yokes the Stimulus `.gamma`
	#     (and other "atmosphere" properties) to the corresponding
	#     properties of the `World`

	redgreen = world.Sine().Inherit( gabor ).Set(
		x = world.width / 4,
		color = [ 1, 0, 0.15 ],  # signal function output will be multiplied by this vector
	)
		
				
	"""
	First we'll define a callback function to handle the gamma value
	that is found by the interactive adjustment procedure.  The callback
	must handle the possibility that its input argument is `None` (which
	is what happens when the user presses the escape key).
	"""#:
	def finish( finalGamma ):
		if finalGamma is None:
			print( '\nNo change: world.gamma is still %r' % list( world.gamma ) )
		else:
			print( '\nSetting world.gamma = %r' % list( finalGamma ) )
			world.gamma = finalGamma
	
	"""
	You can call `Shady.FindGamma()` quite straightforwardly yourself.	
	But for the purposes of this demo, we'll add another layer of complexity:
	we'll set up an `EventHandler` such that `Shady.FindGamma()` gets
	launched every time you hit the enter/return key:
	"""#:
	@world.EventHandler( slot=-1 )
	def PressReturnToStartAdjusting( self, event ):
		if event.type == 'key_release' and event.key in [ 'enter', 'return' ]:
		
			Shady.FindGamma( world, xBlue=xBlue, finish=finish, text=text )
				
	""#>
	print( """
Press the enter/return key to display the linearization pattern and
start adjusting gamma.

While adjusting:

- press enter/return again to finish adjusting and adopt the new settings;
- press escape to exit the adjustment without adopting the new settings;
- press any letter key to report the current gamma setting to the console.
""" )
	Shady.AutoFinish( world )
