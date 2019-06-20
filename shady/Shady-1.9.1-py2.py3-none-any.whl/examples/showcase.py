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

#: ==> Start here to see a little bit of everything Shady can do <==
"""
This script gives a taste of most of Shady's main features.

Unlike most other example scripts, and unlike Shady's default
settings, it will open a small framed window that you can drag
around. Since this is (hopefully) your first Shady demo, we're
going to make the code as simple as possible. That means we
won't give you the chance to override window parameters from
the command-line, which is something all the other demos allow.
Note that rendering performance is nearly always better in a
foregrounded frameless window that covers the whole screen
(Shady's usual default).
"""#.
if __name__ == '__main__':
	import sys
	import Shady
	if sys.argv[ 1: ]:
		# Let's allow command-line arguments if the user wants
		# to use them (e.g. for specifying a --backend) but
		# for now let's hide the code for doing it. The `World()`
		# constructor call should look easy to understand when
		# the user first encounters it.
		cmdline = Shady.WorldConstructorCommandLine( width=1200, height=700, top=50, fullScreenMode=False, frame=True, canvas=True )
		cmdline.Help().Finalize()
		world = Shady.World( gamma=2.2, **cmdline.opts )
	else: # simpler easier-to-understand case
		"""
		Let's set up the "World" in which our Stimuli will reside.  Since we
		don't know you well enough yet to know how you're arranging your
		windows and screens, let's take the unusual step of making the World
		a framed, draggable window.
		"""#:
		world = Shady.World( width=1200, height=700, top=50, frame=True )
		world.MakeCanvas( gamma=2.2 )  # you can also have this step done
		                               # automatically by including canvas=True
		                               # in the World constructor line (along
		                               # with any other physical properties
		                               # like gamma)
		"""
		In future demos, we'll stick closer to Shady's defaults and you can
		manage windowing yourself. If you have a second monitor, maybe you
		would want to supply the command-line option `--screen=2` to put the
		`World` on a second screen. Or, if you have only one screen, maybe
		you could configure your console window to be semi-transparent. Or
		just alt-tab back and forth between console and `World`. You'll
		figure it out.
		"""#.
		
	"""
	Throughout this demo, we'll keep an eye on timing. One simple
	way to do this is to put a `FrameIntervalGauge` on the screen.
	It's just a visible scale that measures frame-to-frame intervals
	in milliseconds (so, for 60 fps it should hover between 16 and
	17). Note that performance is generally much better when the window
	is in the foreground than in the background.  Also, it is usually
	better when the window is frameless and fills the screen, which
	is the way Shady would normally be used.
	"""#:
	gauge = Shady.FrameIntervalGauge( world, corner=[ -1, -1 ] )
	
	"""
	Let's start by creating every visual psychophysicist's favorite
	stimulus, the Gabor patch. The best way to create any stimulus is
	via the `.Stimulus()` method of an existing `World` instance:
	"""#:
	gabor = world.Stimulus(
		size = 300,                # size in pixels (if you want a rectangular
		                           # shape, you can pass [width, height] here) 
		             
		position = [ -200, +200 ], # in pixels relative to the World's origin
		                           # (which is determined by the World's .anchor
		                           # property)
		
		signalFunction = Shady.SIGFUNC.SinewaveSignal, # there's only one built-in
		                                               # signal function, but you 
		                                               # can define more. The value
		                                               # of this property should
		                                               # actually just be a numeric
		                                               # constant (in this case, 1).
		
		signalAmplitude = 0.5,     # the .backgroundColor is 0.5 by default, so
		                           # if we add 0.5 * a sinewave signal to that, we
		                           # get a signal that ranges between 0 and 1. It's
		                           # generally best to use .signalAmplitude to ensure
		                           # contrast is at maximum, and then manipulate the
		                           # .normalizedContrast property to fade from there.
		
		plateauProportion = 0,     # non-negative plateauProportion causes a
		                           # spatial windowing function to be applied
		
		atmosphere = world,        # this uses a couple of shorthand tricks that
		                           # we'll explain in greater detail elsewhere. It
		                           # locks all the background, linearization, and 
		                           # dynamic-range-enhancement parameters to those
		                           # of the World and its canvas
	)

	"""
	Let's animate it too:
	"""#:
	gabor.cx = lambda t: t * 100   # .cx is a shortcut for the horizontal component of gabor.carrierTranslation
	gabor.normalizedContrast = Shady.Oscillator( 0.2 ) * 0.5 + 0.5   # the Oscillator is an example of a
	                                                                 # Shady.Function, which is a callable
	                                                                 # object you can do arithmetic with
	"""
	Square or rectangular patches of solid color are easy:
	"""#:
	rectangle = world.Stimulus(
		size = [ 300, 200 ],
		position = [ +200, +200 ],
		color = [ 0, 0.7, 0 ],     # foreground color green
	)

	"""
	To make a patch circular or elliptical, we specify
	the .plateauProportion and .backgroundAlpha:
	"""#:
	ellipse = world.Stimulus(
		size = [ 300, 200 ],
		position = [ -200, -200 ],
		color = [ 1, 0, 0 ],       # foreground color red
		plateauProportion = 1,     # it's plateau all the way to the edge, so the edge is sharp (but curved)
		backgroundAlpha = 0,       # transparent background (NB: not a good idea for linearized stimuli)
	)
	# 
	# You can also use the method world.Patch() which
	# is simply a convenience wrapper around world.Stimulus()
	# that sets color=1 and backgroundAlpha=0 by default.

	"""
	So far our stimuli haven't needed third-party packages. But
	from now on, we will need the `numpy` package, to manipulate
	arrays of numbers.
	"""#:
	Shady.Require( 'numpy' ) # die with an informative error if this is missing

	"""
	Let's add a field of dots, demonstrating how a single Stimulus
	may contain multiple independently-moving shapes. You have to
	change the .drawMode and then set the .points property. The
	latter can be an n-by-2 array of coordinates, or a sequence
	of complex numbers. A NaN in the sequence of points indicates
	a break in drawing (a place where the pen is taken off the
	paper, so to speak):
	"""#:
	field = world.Stimulus(
		size = [ 300, 200 ],
		position = [ 200, -200 ],
		color = [ 0, 0, 0 ],
		drawMode = Shady.DRAWMODE.POLYGON,
		smoothing = 0,
	)

	nDots = 50
	nSides = 20
	polygonRadius = 3

	import numpy
	positions  = numpy.random.uniform( [ 0, 0 ], field.size, size=[ nDots, 2 ] )
	velocities = numpy.random.uniform( [ -100, -100 ],  [ +100, +100 ], size=[ nDots, 2 ] )
	shape = Shady.ComplexPolygonBase( nSides ) * polygonRadius # this handily includes the NaN break between polygons

	field.points = lambda t: Shady.Real2DToComplex( ( positions + velocities * t ) % field.size ) + shape
	# Real2DToComplex converts nDots-by-2 real coordinates into nDots-by-1
	# complex, and `shape` is 1-by-(nSides+1) complex.  numpy "broadcasting"
	# in the `+` operator automatically does the magic of creating multiple
	# polygons at different locations.

	"""
	The dots initially have a radius of 3 pixels. Let's make them bigger:
	"""#:
	shape *= 2
	# this is possible because we're working in the same namespace in which
	# we also created the function to specify the `.points` property, and
	# that function contains a baked-in "global" reference to `shape` in that
	# namespace. Therefore, changes to the `shape` variable here will affect
	# the function. This behavior is a subtle (and sometimes counterintuitive)
	# feature of Python, but very powerful and well worth taking time to learn.

	"""
	From now on, we'll also need the `Image` module from the `pillow` or `PIL`
	package, since it is used under the hood whenever we want to load from, or
	save to, an image file.
	"""#:
	Shady.Require( 'Image' ) # die with an informative error if this is missing

	"""
	We'll create a Stimulus from an image file from disk. Our default
	example is a multi-frame GIF, so we'll demonstrate texture animation
	into the bargain:
	"""#:
	filename = Shady.EXAMPLE_MEDIA.alien1
	image = world.Stimulus( filename, position=[ 0, 0 ], frame=lambda t: t * 16 )

	"""
	Let's go for a walk. The `Shady.Dynamics` sub-module contains
	a number of objects that can be used for dynamic property setting.
	The general-purpose `Function` class provides a callable object that
	can be modified by ordinary arithmetic as well as other transformations.
	`Integral` and `Derivative` are wrappers around `Function`
	construction: they provide stateful memory and can hence be used to
	make discrete numeric approximations to the integrals and derivatives
	of arbitrary functions.  `Oscillator` is a wrapper around
	`Integral`: the `Function` object is transformed so that it produces
	sinusoidal oscillations. 
	
	Here we demonstrate how you can include `Function` objects in
	arithmetic expressions: the output of `Oscillator` is multiplied by
	a scalar:
	"""#:
	radius = min( world.size ) / 2.0
	period = 6.0
	image.Set(
		position = Shady.Oscillator( 1. / period, phase_deg=[ 0, -90 ] ) * radius,
		rotation = Shady.Integral( 360.0 / period ),
		anchor = ( 0, -1 ),
		z = -0.1
	)

	"""
	The `Shady.Dynamics` sub-module also provides a handy `StateMachine`
	for changes that follow piecewise logic in time.
	
	The `StateMachine` object is also callable. It takes a single
	argument, time `t`, and this is one of the acceptable prototypes
	for an `AnimationCallback`---in fact, it's the one that allows direct
	assignment to the `.Animate` attribute.
	"""#:
	class Noisy( Shady.StateMachine.State ):
		duration = 0.5
		next = 'Solid'
		def onset( self ):
			rectangle.Set( color=-1, noiseAmplitude=-0.5 )
			
	class Solid( Shady.StateMachine.State ):
		duration = 4
		next = 'Noisy'
		def onset( self ):
			rectangle.Set( color=numpy.random.uniform( size=3 ), noiseAmplitude=0 )

	rectangle.Animate = Shady.StateMachine( Noisy, Solid )

	"""
	Now let's try text.  Text rendering is an optional extra that needs
	`numpy` and `pillow`. Also, if `matplotlib` is installed, that will
	get imported too, to enable access to your system fonts. Font setup
	may take several seconds if you're doing this for the first time,
	which is one of the reasons that text rendering is not enabled by
	default.  To enable it, we simply say:
	"""#:
	import Shady.Text

	"""
	All set? Creating a text stimulus is easy enough:
	"""#:
	message = world.Stimulus(
		position = ellipse.Place( 0, 0 ),
		text = 'Hello world!\nThis is Shady.',
		text_align = 'center',     # this is a way of addressing the text sub-properties
		                           # during initialization, before the `.text` instance has
		                           # been created...
	)
	message.text.align = 'center'  # but this is the canonical way of manipulating sub-
	                               # properties of the `.text` object once it is created.

	"""
	Although `message.text` is an object with properties of its own,
	assigning a string to it is a useful shorthand for assigning to
	the `.text.string` sub-property.  And the `.text` property can
	be dynamic.  So, for example:
	"""#:
	message.text = lambda t: 'It has been\n%d seconds\nsince the World was created.' % t

	"""
	Did that have an impact on the frame interval gauge? And on the
	smoothness of the rest of the animations?  Be warned: whenever
	the text changes, as it now does once per second, the image has
	to be re-rendered on the CPU and then transferred to the GPU.
	This is an inefficient approach by Shady's usual standards, so
	it may affect timing performance.
	"""#:

	"""
	The text doesn't quite fit into the ellipse. So, hold on
	a second:
	"""#:
	message.scaling = Shady.Transition( start=1.0, end=0.5, duration=2.0 )
	# or, rather, two seconds.

	""" 
	The final Stimulus trick we'll consider here is video. We'll
	need the `cv2` module, from `opencv-python`. This is slightly
	less stable across platforms and versions than Shady's other
	dependencies, so your mileage may vary. Therefore, like text
	rendering, we have made video decoding an optional extra. So
	it needs to be enabled explicitly, as follows:
	"""#:
	import Shady.Video

	"""
	Note that video decoding will be done on the CPU, and each
	new frame is transferred from the CPU to the GPU---even more
	so than dynamic text, this is a very inefficient approach by
	Shady's usual standards.  As a result, frame timing performance 
	will often suffer, especially if the video is large.
	
	Whenever precise frame timing matters, examine your timing
	performance critically, using the `FrameIntervalGauge` and/or
	`Shady.PlotTimings`.
	"""#:

	"""
	Now let's create a video stimulus:
	"""#:
	filename = Shady.EXAMPLE_MEDIA.fish

	fish = world.Stimulus(
		video = filename,    # could also use an integer here if you want
		                     # the video to be acquired live from a camera
		scaling = 0.25,
		position = rectangle.Place( 0, 0 ),
	)

	import os
	caption = world.Stimulus(
		text = os.path.basename( filename ),
		position = lambda t: fish.Place( 0, -1.1 ),
		anchor = [ 0, +1 ],
		text_size = 20,
		text_bg = [ 0, 0, 0, 0.5 ],
	)

	"""
	...and play it:
	"""#:
	fish.video.Play( loop=True )

	"""
	Well, it's been fun.  For a list of other interactive
	demos, you can launch Python as follows::
	
	    python -m Shady list
	
	Meanwhile, here is some version information:
	"""#>
	print( '\n\n' )
	world.ReportVersions()
	print( '\nPress Q or escape to close the window.' )
	
		
	Shady.AutoFinish( world )
