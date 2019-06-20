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

#: Need to guarantee rounded dots?  Animate multiple polygons!
"""
This demo shows how it is very easy, and still fairly
computationally inexpensive, to animate a dot stimulus
in which each "dot" is a polygon.  It uses the POLYGON
draw mode, and our setup will be aided by the
`ComplexPolygonBase` utility function.

Using polygons with a high number of sides (say, 20)
is the only way to guarantee round-shaped dots. The
simpler approach of the `dots1` demo, using the POINTS
draw mode and `smoothing=True`, is not guaranteed to
produce round dots---it depends on your graphics
hardware and drivers.
"""#.
if __name__ == '__main__':
	"""
	First let's parse the command-line arguments for
	this demo:
	"""#:
	import Shady
	# All the usual World-construction ones we use in most demos:
	cmdline = Shady.WorldConstructorCommandLine( canvas=False )
	# And some that are specific to this demo:
	ndots  = cmdline.Option( 'ndots', 300,   type=int, container=None, doc="Number of shapes.  Ensure (nsides+1)*ndots <= %d" % Shady.Rendering.MAX_POINTS )
	nsides = cmdline.Option( 'nsides',  5,   type=int, min=3, container=None, doc="Number of sides.  Ensure (nsides+1)*ndots <= %d" % Shady.Rendering.MAX_POINTS )
	radius = cmdline.Option( 'radius', 25.0, type=( int, float ), container=None, doc="Half-width of each shape, in pixels." )
	spin   = cmdline.Option( 'spin',    0.2, type=( int, float ), container=None, doc="Spin the shapes at this speed (revolutions per second)." )
	gauge  = cmdline.Option( 'gauge', False, type=bool,  container=None, doc="Whether or not to show a `FrameIntervalGauge`." )
	cmdline.Help().Finalize()
	Shady.Require( 'numpy', 'Image' ) # die with an informative error if either is missing

	if ( nsides + 1 ) * ndots > Shady.Rendering.MAX_POINTS: raise ValueError( '(nsides + 1) * ndots cannot exceed %d' % Shady.Rendering.MAX_POINTS )
	
	"""
	Create a World:
	"""#:
	w = Shady.World( **cmdline.opts )
	if gauge: Shady.FrameIntervalGauge( w )
	
	"""
	Create a Stimulus to act as a container for the shapes. For fun, we're
	going to give this one a background image:
	"""#:
	field = w.Stimulus( Shady.PackagePath( 'examples/media/waves.jpg' ), size=w.size, visible=1 )
	# And now, a slightly awkward manipulation of carrier parameters, to make the image fill
	# the screen without stretching the coordinate system in which the shapes are defined (that's
	# what would happen if we were to change .envelopeScaling)
	field.carrierTranslation = ( field.envelopeSize - field.textureSize ) // 2 
	field.carrierScaling = max( field.envelopeSize.astype( float ) / field.textureSize )
	
	"""
	Set up the dynamic that draws the shapes:
	"""#:
	shape = Shady.ComplexPolygonBase( nsides )
	import numpy
	location = numpy.random.uniform( low=[   0,   0 ], high=field.size,    size=[ ndots, 2 ] )
	velocity = numpy.random.uniform( low=[ -30, -30 ], high=[ +30, -150 ], size=[ ndots, 2 ] )
	func = Shady.Integral( lambda t: velocity ) # we could say just Shady.Integral( velocity ) 
	                                            # but then we wouldn't be able to change the 
	                                            # velocity on-the-fly
	func += location
	func %= field.size # wrap around the field, pacman-style
	func.Transform( Shady.Real2DToComplex )      # ndots-by-1 complex
	func += lambda t: radius * shape * 1j ** ( 4.0 * spin * t )  # 1-by-(sides+1) complex
	# numpy broadcasting in the `+` operator does the rest.
	# It is possible to assign a sequence of complex numbers to the `.points` property,
	# so we will leave the `func` output in complex form.
	
	"""
	Apply it:
	"""#:
	field.Set( points=func, drawMode=Shady.DRAWMODE.POLYGON, visible=1 )

	"""
	Note that the `lambda` function we defined in the last line of our
	setup is continually accessing, on every frame, three variables in
	the current namespace, called `radius`, `shape` and `spin`. This
	means that any manipulations you make to these variables, at the
	current command-line, will immediately affect the stimulus.
	
	Try playing with them.  Examples of some things to try::
	
		radius *= 2
		spin /= 2
		shape = Shady.ComplexPolygonBase( 3 )   # or whatever
		
		shape = Shady.ComplexPolygonBase( 3, joined=True )
		field.Set( drawMode=Shady.DRAWMODE.LINE_STRIP, penThickness=1 )
		
		
	"""#>
	Shady.AutoFinish( w ) # Finish up the demo (in case we're not running with `python -m Shady`)
