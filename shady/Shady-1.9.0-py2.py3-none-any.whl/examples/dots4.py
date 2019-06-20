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

#: Interactive real-time demo of the power of multi-element stimuli
"""
This demo shows how large numbers of independent elements can be
animated and made to respond in real time.

A single `Shady.Stimulus`, while usually rendered as a rectangle,
can be rendered as anything up to 20,000 independent points. If these
are managed as a `numpy` array, and manipulated in a "vectorized" way
such that the bulk of the arithmetic operations happen in compiled
binaries, these points can be animated in quite sophisticated ways,
well within 60 fps deadlines (verify this with `--gauge` and/or
`--debugTiming` provided you have numpy and matplotlib installed)

An `n`-sided polygon uses up `n+1` points, so for polygons, when you
specify `--nsides=3`  or above, the number of independent polygons
`--ndots=m` is limited by `(n+1)*m <= 20000`

A line segment uses up just 2 points, so for line segments, you can
specify either `--nsides=2` or `--nsides=1` (both are equivalent)
and then the number of independent segments can be anything up to
`--ndots=10000`.

Move the mouse around / touch the touch-screen to interact with the
shapes.
"""#.
if __name__ == '__main__':

	import Shady

	"""
	Parse the command-line for the usual World construction options:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine()

	"""
	..and add a few options that parameterize the demo:
	"""#:
	ndots  = cmdline.Option( 'ndots' , 3000,  type=int, container=None, doc='Number of independent shapes.' )
	nsides = cmdline.Option( 'nsides',    2,  type=int, min=1, container=None, doc='\n1 or 2 for line segments:  ndots <= %d\n3+ for polygons:           ndots*(nsides+1) <= %d' % ( Shady.Rendering.MAX_POINTS / 2, Shady.Rendering.MAX_POINTS ) )
	radius = cmdline.Option( 'radius',   10,  type=( int, float ), container=None, doc='Dictates the half-width of each shape, in pixels.' )
	spin   = cmdline.Option( 'spin',    0.2,  type=( int, float ), container=None, doc='Max. number of revolutions per second of each shape around its own center.' )
	energy = cmdline.Option( 'energy',  0.3,  type=( int, float ), container=None, doc='Larger numbers make the storm winds blow harder.' )
	dims   = cmdline.Option( 'dims',  ( 0, 1 ),  type=( tuple, list ), minlength=2, maxlength=2, container=None, doc='Which two of the three dimensions of the attractor should\nbe plotted? Possibilities:  0,1   1,0   0,2   2,0   1,2   2,1' )
	gauge  = cmdline.Option( 'gauge', False,  type=bool,  container=None, doc="Whether or not to show a `FrameIntervalGauge`." )
	cmdline.Help().Finalize()
	Shady.Require( 'numpy' ) # die with an informative error if this is missing


	"""
	First let's create a shape.  For nsides > 2 we'll use a polygon,
	delimited by a NaN. A special case will be nsides=1 or nsides=2
	both of which will be interpreted to mean that each shape is a single
	line segment. In that case the "LINES" draw-mode will be used, and
	that draws a separate line segment connecting the points in each
	successive pair, so we can omit the NaN-break between shapes (we don't
	have to, but it increases the max number of shapes we can use by 50%).
	"""#:
	if nsides == 1: nsides = 2
	shape = Shady.ComplexPolygonBase( nsides, appendNaN=nsides>2 ) # 1-by-(nsides+1) complex
	if shape.size * ndots > Shady.Rendering.MAX_POINTS:
		raise ValueError( 'too many points: (nsides + 1) * ndots should be <=%d' % Shady.Rendering.MAX_POINTS )

	"""
	Create the World according to the usual command-line opts
	"""#:
	w = Shady.World( bg=0.2, **cmdline.opts )
	if gauge: Shady.FrameIntervalGauge( w )

	"""
	Create a field on which to draw multiple copies of the shape:
	"""#:
	field = w.Stimulus(
		anchor = -1,                # position its bottom-left corner...
		position = w.Place( -1 ),   # in the bottom-left corner of the window
		size = w.size,              # and (potentially) fill the window
		noise = -0.5,               # with high-contrast uniform noise...
		drawMode = Shady.DRAWMODE.POLYGON if nsides > 2 else Shady.DRAWMODE.LINES,  # ...but only where the shapes are
	)

	"""
	Define a center to the maelstrom, and allow the user 
	to move it with the mouse or touch-screen:
	"""#:
	w.eyeOfStorm = field.Place( 0, 0, False )
	@w.EventHandler( slot=-1 )
	def Interact( self, event ):
		if event.type in [ 'mouse_motion', 'mouse_press' ]: # and 'left' in event.button.split():
			self.eyeOfStorm = Shady.RelativeLocation( [ event.x, event.y ], field )


	"""
	Choose which two dimensions of the 3-D attractor
	will be projected onto the screen:
	"""#:
	realdim, imagdim = dims
	scale = min( w.size ) / 25.0
	def OriginXYZ():
		global realdim, imagdim # just to make things more readable later on
		realdim, imagdim = dims
		out = [ 0.0, 0.0, 0.0 ]
		out[ realdim ], out[ imagdim ] = w.eyeOfStorm
		if 2 in dims: out[ 2 ] -= scale * 10.0
		return out

	"""
	Initialize the position and angular velocity of each shape:
	"""#:
	import numpy
	start = [ OriginXYZ()[ i ] + scale * numpy.random.uniform( -10, 10, ndots ) for i in range( 3 ) ]  # 3-by-ndots real coords X,Y,Z
	spin = numpy.random.uniform( -spin, spin, [ ndots, 1 ] )  # ndots-by-1 real

	"""
	Set up the differential equations of the attractor:
	"""#:
	a, b, c = 10.0, 28.0, 8.0 / 3.0  # the Lorenz attractor's three magic numbers
	denom = 2; a /= denom; b /= denom; c /= denom # necessary if using Integral(integrate='trapezium') which is the default; comment out if using Integral(integrate='rectangle')

	def deriv( t ):
		x, y, z = tap()	# defined below: will provide a view into the previous value of the integral of this function
		x0, y0, z0 = OriginXYZ()
		x = ( x - x0 ) / scale
		y = ( y - y0 ) / scale 
		z = ( z - z0 ) / scale
		d_dt = [  a * ( y - x ),     x * ( b - z ) - y,    x * y - c * z  ]  # Lorenz attractor equations
		return energy * scale * numpy.vstack( d_dt )  # output is 3-by-ndots real velocities dX/dt, dY/dt, dZ/dt

	"""
	Build a `Shady.Function` object that integrates
	the above function:
	"""#:
	func = Shady.Integral( deriv, initial=start )
	tap = func.Tap( initial=start ) # allows the Function values to be inspected at this stage of processing
	func.Transform( lambda coord: ( coord[ realdim ] + 1j * coord[ imagdim ] )[ :, None ] )  # transform 3-by-ndots real to ndots-by-1 complex
	func += lambda t: radius * shape * 1j ** ( 4.0 * spin * t ) # add nsides-by-ndots independently spinning shapes

	"""
	Go!
	"""#:
	field.points = func  # dynamic value assignment to the managed `Stimulus` property `.points`
	
	""#>
	Shady.AutoFinish( w )
