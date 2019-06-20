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

#: A simple random-dot stimulus
"""
This demo shows the simplest way of drawing dot stimuli,
which is to set the `.drawMode` property to
`Shady.DRAWMODE.POINTS` and then manipulate the `.points`
property.   The visual quality of the results will depend
on your graphics drivers.  To achieve greater control over
dot appearance, see the other dots demos (`dots2`, `dots3`
and `dots4`).
"""#.

if __name__ == '__main__':
	"""
	First let's wrangle the command-line options:
	"""#:
	
	import Shady
	cmdline = Shady.WorldConstructorCommandLine( canvas=False )
	ndots     = cmdline.Option( 'ndots',    300, type=int,  container=None, doc="Number of dots (may not exceed %d)." % Shady.Rendering.MAX_POINTS )
	bounce    = cmdline.Option( 'bounce', False, type=bool, container=None, doc="If True, implement some rudimentary physics to make the dots bounce off each other." )
	gauge     = cmdline.Option( 'gauge',   True, type=bool, container=None, doc="Whether or not to show a `FrameIntervalGauge`." )
	thickness = cmdline.Option( 'thickness', 20, type=( int, float ), container=None, doc="Value for the `.penThickness` property, dictating the size of the dots." )
	smooth    = cmdline.Option( 'smooth',  True, type=bool, container=None, doc="""If True, flag the dots as "smooth". This may make them round instead of square, or it may have no effect - unfortunately this is driver-dependent. If you want to guarantee round dots you'll have to use small polygons instead (see dots3 and dots4 demos) or separate `Stimulus` instances (dots2).""" )
	cmdline.Help().Finalize()
	Shady.Require( 'numpy' ) # die with an informative error if this is missing

	"""
	Create a World and, if requested, a frame interval gauge:
	"""#:
	w = Shady.World( **cmdline.opts )
	if gauge: Shady.FrameIntervalGauge( w )
	
	"""
	Now a single Stimulus that will host our random dots.
	We'll use the `POINTS` drawing mode.
	"""#:
	field = w.Stimulus( size=w.size, color=1, drawMode=Shady.DRAWMODE.POINTS, penThickness=thickness, smoothing=smooth )
	
	"""
	To draw the points, we'll have to set the `.points`
	property.
	"""#:
	import numpy
	location = numpy.random.uniform( low=[   0,   0 ], high=field.size,    size=[ ndots, 2 ] )
	velocity = numpy.random.uniform( low=[ -30, -30 ], high=[ +30, -150 ], size=[ ndots, 2 ] )
	field.points = ( Shady.Integral( velocity ) + location ) % field.size

	
	"""
	Now, for a bit of fun, we'll define a couple of functions
	that allow the dots to bounce off each other.
	"""#:
	physics = dict( exponent=10, closest=10, coefficient=800 )
	def RepulsionForces( t=None ):
		positions = field.pointsComplex
		vectors = positions[ None, : ] - positions[ :, None ]
		magnitudes = numpy.abs( vectors )
		degenerate = magnitudes < 1e-4
		nondegenerate = ~degenerate
		vectors[ nondegenerate ] /= magnitudes[ nondegenerate ] # vectors are now unit vectors
		magnitudes[ degenerate ] = numpy.inf
		magnitudes = numpy.clip( magnitudes - field.penThickness / 2.0, physics[ 'closest' ], numpy.inf )
		magnitudes /= physics[ 'closest' ]
		magnitudes **= -physics[ 'exponent' ] # now we have inverse square (or whatever power) distances, with 0s on diagonal
		forces = magnitudes * vectors * physics[ 'coefficient' ]
		forces = forces.sum( axis=0 )
		forces = Shady.ComplexToReal2D( forces )  # n-by-2 real-valued output
		return forces
	def Bounce( **kwargs ):
		physics.update( kwargs )
		field.points = ( Shady.Integral( Shady.Integral( RepulsionForces ) + velocity ) + field.points ) % field.size

	if bounce: w.Defer( Bounce )
	# .Defer() will ensure that the function gets called at the end of
	# the next frame (this ensures that field.pointsComplex, which
	# RepulsionForces() relies on, has already had a value assigned to it

	"""
	If you requested this with the `--bounce` command-line option
	then the points should already be bouncing off each other.
	If not, you can manually trigger it if you want, by calling
	`Bounce()`.  Either way, our dots demo is done.
		
	Note that `drawMode=POINTS` is the simplest way of creating
	dot patterns, but not necessarily the most powerful. Setting
	`smoothing=True` should in principle make them round, but
	whether it successfully does so is dependent on your graphics
	driver: they may stubbornly remain square.  The best way of
	guaranteeing the shape of your dots is to draw them as
	tiny polygons (with a high number of sides, if you want them
	to look round).  This can be explored in the `dots3` and
	`dots4` demos.  Another option is to make each "dot" an
	independent Stimulus - but as the `dots2` demo shows, you
	have to worry much more about timing performance in that case.
	"""#:
	
	"""
	By the way: if you're not pleased with the frame rate of your
	colliding dots, and you're reading this console in the foreground,
	try switching to the World as your main window. This will put
	Shady in charge of synchronizing frame buffer swaps and likely
	lead to significant improvements in performance.
	"""#>
		
	Shady.AutoFinish( w )
