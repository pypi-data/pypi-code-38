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

#: How many separate `Stimulus` instances can we manage?

"""
In the `dots1` demo we saw a simple way of presenting a large
number of independently-moving elements. One of its limitations
was that the appearance of the dots could not be guaranteed
(some graphics drivers can present rounded dots, and others
cannot---spoiler alert: the `dots3` demo has the best answer
to this particular problem).   Another limitation is that the
dots are completely homogeneous in their appearance (because
they are part of the same `Stimulus`, hence the same
properties apply to all of them).

This demo explores the idea of controlling each and every
"dot" as a separate `Stimulus`.  This places much greater
demand on Shady: while it's easy and cheap to manipulate
several thousand shapes in the same `Stimulus`, rendering
hundreds of separate `Stimulus` instances pushes Shady
much more quickly to its performance limits, due to the
accumulated small overhead costs.  Nonetheless it is
worth exploring where, exactly, these limits lie, and some
of the tricks we can use to push them.  This demo creates
multiple circular stimuli, provides three different
strategies for updating their positions independently of
each other, and provides various tools for analyzing the
relative efficiency of these strategies under different
conditions.
"""#.
import sys
import Shady

"""
Let's start by defining a subclass of `World`. 

The base `World` class has a `Prepare()` method. When you
construct a `World`, any constructor arguments that are not
recognized (either as construction options or `World`
properties) are passed through to the `Prepare()` method.
In the base class, all that happens is that they get printed
to the console.  Here in our subclass, we will define the 
`Prepare()` method to perform stimulus setup.  The advantage
of doing it here is that `Prepare()` is guaranteed to run
in the same thread as the `World` rendering loop, so there
are no `.Defer`red actions.

"""#:
class DotWorld( Shady.World ):
	"""
	Here's the Prepare method:
	"""#:
	def Prepare( self, ndots=150, mode='batch', gauge=False, textured=False, swap=1, blur=True, radius=25 ):
		import numpy
		self.anchor = -1
		self.Set( gamma=2.2, bg=0.5 )
		self.dots = [ self.Stimulus(
			name = 'dot%04d',
			size = radius * 2,
			color = numpy.random.rand(3),
			bgalpha = 0,
			pp = ( float( i ) / ndots )  if blur else 1,
			debugTiming = False,
			atmosphere = self,
		) for i in range( ndots ) ]
		self.start = numpy.array( [ self.Place( numpy.random.uniform( -1, 1, size=2 ) ) for dot in self.dots ] )
		self.velocity = numpy.random.uniform( low=[ -30, -30 ], high=[ +30, -150 ], size=self.start.shape )
		self.batch = self.CreatePropertyArray( 'envelopeTranslation', self.dots ) # could use 'envelopeTranslation' or 'envelopeOrigin'

		# for manipulating positions all in one batch array operation:
		self.allPositions = self.batch.A[ : , :2 ] # allows us to use either .envelopeTranslation or .envelopeOrigin
		self.allPositions[ : ] = self.start 
		
		# for manipulating positions in a single loop over arrays:
		self.each = list( zip( self.allPositions, self.start, self.velocity ) )
		
		# for manipulating positions by attaching a dynamic to each and every stimulus:
		def MakeDynamic( start, velocity, worldSize ): return lambda t: ( start + velocity * t ) % worldSize
		self.lambdaFunctions = [ MakeDynamic( start, velocity, self.size ) for _, start, velocity in self.each ]
		
		if gauge: Shady.FrameIntervalGauge( self, color=0 )
		self.master = self.dots[ -1 ]
		self.master.ShareProperties( self.dots, 'envelopeSize envelopeScaling textureID textureSlotNumber useTexture' ) 
		self.numberOfActiveStimuli = len( self.dots )
		if textured: self.ToggleTextures()
		self.Swap( swap )
		self.UpdateMode( mode )
	"""
	One of the key things our `Prepare()` method did is create
	a `PropertyArray` object called `self.batch`.  Its attribute
	`self.batch.A` is a `numpy` array containing a packed
	representation of the `.envelopeTranslation` arrays of all
	the "dot" stimuli. So, while we still have the option of
	addressing their positions individually, we now also have
	the more efficient option of addressing them collectively in
	a single array operation.
	"""#:
	
	"""
	Here's a potential `AnimationCallback`: it updates the dot
	positions one by one, in a Python loop.
	"""#:
	def AnimateEach( self, t ):
		for position, start, velocity in self.each[ :self.numberOfActiveStimuli ]:
			position[ : ] = ( start + velocity * t ) % self.size
		
	"""
	Here's an alternative `AnimationCallback`: it updates the dot
	positions all in one array operation, taking advantage of the
	`PropertyArray` we created.
	"""#:
	def AnimateAllTogether( self, t ):
		self.allPositions[ : ] = ( self.start + self.velocity * t ) % self.size
		
	"""
	Here's a method that allows us to switch the way we update
	`Stimulus` positions.  'multi' mode uses an individual function
	call for each stimulus (dynamic value assignment); 'loop' mode
	uses `AnimateEach`, a single animation callback that updates
	the stimuli in a Python loop; and 'batch' mode uses
	`AnimateAllTogether`, a single animation callback that updates
	everything in one single `numpy` array operation.
	
	To help us distinguish which mode we're in, we'll turn the
	`World` green for multi mode, red for loop mode and blue for
	batch mode.
	"""#:
	def UpdateMode( self, mode ):
		if mode == 'multi':   # least efficient
			self.SetAnimationCallback( None )
			self.clearColor = [ 0, 0.4, 0 ]
			for dot, lambdaFunction in zip( self.dots, self.lambdaFunctions ):
				dot.xy = lambdaFunction
		elif mode == 'loop':  # intermediate
			self.SetAnimationCallback( self.AnimateEach )
			self.clearColor = [ 0.4, 0, 0 ]
			for dot in self.dots: dot.SetDynamic( 'xy', None ) 
		elif mode == 'batch':  # most efficient
			self.SetAnimationCallback( self.AnimateAllTogether )
			self.clearColor = [ 0, 0, 0.4 ]
			for dot in self.dots: dot.SetDynamic( 'xy', None ) 
		else:
			raise ValueError( 'unrecognized mode %r' % mode )
		self.mode = mode
		self.Report()
	
	def Report( self ):
		print( 't=% 7.3f,  nTotal=%d,  nActive=% 4d,  mode=%r, ' %
			( self.t, len( self.dots ), self.numberOfActiveStimuli, self.mode ) )
			
	"""
	The following method will allow us to investigate the performance
	impact of texture rendering:
	"""#:
	def ToggleTextures( self ):
		if self.master.source is None:
			# first-time setup
			self.master.LoadTexture( Shady.PackagePath( 'examples/media/face.png' ), False )
			self.master.cr = Shady.Clock( speed=90 )  # the master rotates - see if you can spot it
		else:
			# toggle texture on or off
			self.master.useTexture = not self.master.useTexture
	
	"""
	And now here's a method that will allow us (at least on Windows)
	to halve our frame-rate and thereby hopefully homogenize it, if
	our dots are pushing the performance envelope too hard:
	"""#:
	def Swap( self, nFrames ):
		msg = 'calling SetSwapInterval( %r )' % nFrames
		if nFrames > 1 and not sys.platform.lower().startswith( 'win' ):
			msg += ' --- NB: values >1 might not be respected on this system'
		print( msg )
		self.SetSwapInterval( nFrames )  # needs accelerator (and seems to fail on mac)
		
	"""
	Finally, an event-handler. There are multiple ways to implement
	these (see the `events` demo) but since we're already defining
	a subclass the most straightforward way is simply to overshadow
	the `HandleEvent` method:
	"""#:
	def HandleEvent( self, event ):
		if event.type == 'key_release':
			if event.key in [ 'q', 'escape' ]: self.Close()
			elif event.key in [ 't' ]: self.ToggleTextures()
			elif event.key in [ 'm' ]: self.UpdateMode( 'multi' )
			elif event.key in [ 'l' ]: self.UpdateMode( 'loop' )
			elif event.key in [ 'b' ]: self.UpdateMode( 'batch' )
			elif event.key in [ '1', '2' ]: self.Swap( int( event.key ) )
			elif event.key in [ '-', '+', '=' ]:
				if event.key in [ '+', '=' ]: self.numberOfActiveStimuli += 50
				elif event.key in    [ '-' ]: self.numberOfActiveStimuli -= 50
				self.numberOfActiveStimuli = min( len( self.dots ), max( 0, self.numberOfActiveStimuli ) )
				for dot in self.dots[ :self.numberOfActiveStimuli ]: dot.Enter()
				for dot in self.dots[ self.numberOfActiveStimuli: ]: dot.Leave()
				self.Report()
""#.
if __name__ == '__main__':
	"""
	OK, that's the class definition done. Let's sort out command-line
	options:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( canvas=False )
	cmdline.Option( 'ndots',    150,   type=int,  doc='''Number of shapes. Unlike the other "dots" demos, each distinct "dot" is a separate, independent `Stimulus` instance. (This will quickly tend to push the boundaries of Shady's timing performance.)''' )
	cmdline.Option( 'mode',  'batch',  type=str, strings=[ 'multi', 'loop', 'batch' ], doc="Select one of three modes in which to update stimulus positions (each with a different overhead cost)." )
	cmdline.Option( 'gauge',    True,  type=bool, doc="Whether or not to show a `FrameIntervalGauge`." )
	cmdline.Option( 'textured', False, type=bool, doc="Whether or not to render a texture on each `Stimulus` (if so, one texture is loaded, and shared between all `Stimulus` instances)." )
	cmdline.Option( 'blur',     True,  type=bool, doc="Whether or not to vary the `.plateauProportion` among stimuli." )
	cmdline.Option( 'swap',     1,     type=int, min=1, doc="Swap interval, in physical frames.\nUsually swap=1 -> 60 fps;  swap=2 -> 30 fps\n(swap>1 might only work in Windows)" )
	cmdline.Option( 'radius',   25,    type=( int, float ), min=1, doc="Radius of each Stimulus, in pixels." )
	# since we haven't said `container=None` for any of these options, they will all end
	# up in the `cmdline.opts` dict, along with all the standard `World`-construction
	# items. Our `World` constructor will not recognize them, so it will pass them through
	# to the `Prepare` method, which we *have* implemented to recognize them.
	cmdline.Help().Finalize()
	Shady.Require( 'numpy', 'Image' ) # die with an informative error if either is missing
	
	"""
	So now all we have to do is create and run the World subclass:
	"""#:
	w = DotWorld( **cmdline.opts )
	
	""#>
	print( """
Keyboard commands:	

    T        Toggle texture on/off
  
M / L /B     Select 'multi', 'loop' or 'batch' mode for
             stimulus position updates
             
  1 / 2      SetSwapInterval to 1 or 2 physical frames
             (usually:  1 -> 60fps;  2 -> 30fps; may only
             work on Windows)

  - / +      Reduce / increase the number of stimuli rendered
             on each frame (up to the maximum specified by the
             --ndots option)
             
Q / escape   Close window
""" )
	Shady.AutoFinish( w )
