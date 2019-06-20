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

#: Testing the properties of our GPU-side random number generator
"""
This demo tests properties of the random-number generator (RNG)
in our fragment shader.  Since we want independent random values
generated for each pixel, and the fragment shader processes pixels
in parallel without being able to pass a state from one to the
other, building a good RNG is a challenge.

This test generates a screen full of dynamic noise until the user
presses a key. Then it takes a screenshot, closes down the World,
and plots (assuming you have matplotlib installed) a histogram of
the screenshot pixel values.

Results are easiest to interpret when the noise is generated without
any gamma correction. The test can be parameterized using the --bg
and --noise command-line parameters, which affect the
`Stimulus.backgroundColor` and `Stimulus.noiseAmplitude` of the
canvas, respectively.

If your graphics card, drivers and operating system make GLSL 3.3+
shader functions available (which is the case on most of the modern
Windows systems we have tested) then our RNG is of pretty good
quality.  If these functions are not available, then the histograms
are not quite as beautiful and there will sometimes be detectable
structure in the noise---this is the case on macOS by default,
because macOS does not allow legacy GLSL 1.2 code to be mixed with
more modern OpenGL code. On macOS, it may therefore be worth
explicitly disabling legacy OpenGL features with the constructor
argument `legacy=False` (compare the results of this demo with
the `--legacy=False` command-line option vs `--legacy=True`).
"""#.
import sys
import Shady

"""
Juggle command-line construction options.
"""#:
cmdline = Shady.WorldConstructorCommandLine()
bg    = cmdline.Option( 'bg',    0.5,   type=( int, float, tuple, list ), min=0.0,  max=1.0, minlength=3, maxlength=3,
	doc='This controls the World/canvas `.backgroundColor` property. Supply a scalar to specify a gray luminance level, or an R,G,B triplet to specify a color.' )
noise = cmdline.Option( 'noise', 0.1,   type=( int, float, tuple, list ), min=-1.0, max=1.0, minlength=3, maxlength=3,
	doc='This controls the World/canvas `.noiseAmplitude` property. Supply a scalar to specify a gray luminance level, or an R,G,B triplet to specify a color. Negative values get you a uniform distribution, positive get you a Gaussian distribution.' )
cmdline.Help().Finalize()
Shady.Require( 'numpy' ) # die with an informative error if this is missing
cmdline.opts.update(
	canvas = True,
	threaded = False,
	outOfRangeColor = -1,
	outOfRangeAlpha = -1,
)

"""
Create the World. Replace the default event handler.
Also add a handler that runs just before the window
closes:  any key stops and closes the World, but a
screenshot is taken first.
"""#:
w = Shady.World( **cmdline.opts )

@w.EventHandler
def eh( self, event ):
	if event.type == 'key_press':
		self.Close()

@w.BeforeClose
def NoiseStats():
	w.snapshot = w.Capture()[ :, :, :3 ]
	normalized = w.snapshot / w.dacMax
	print( '\nPixel stats:  Red    Green    Blue' )
	print(   '     min = [ %.3f,  %.3f,  %.3f ]' % tuple( normalized.min( axis=( 0, 1 ) ).flat ) )
	print(   '     max = [ %.3f,  %.3f,  %.3f ]' % tuple( normalized.max( axis=( 0, 1 ) ).flat ) )
	print(   '     std = [ %.3f,  %.3f,  %.3f ]' % tuple( normalized.std( axis=( 0, 1 ) ).flat ) )
	print( '' )
	title = '--bg=%s  --noise=%s' % ( repr( bg ).replace( ' ', '' ), repr( noise ).replace( ' ', '' ) )
	Shady.Histogram( w.snapshot, DACmax=w.dacMax, title=title )

"""
Press any key to stop and analyze the noise.
Remember you'll need to close the histogram
window before you can exit this Python session.
"""#>
Shady.AutoFinish( w, plot=True )
