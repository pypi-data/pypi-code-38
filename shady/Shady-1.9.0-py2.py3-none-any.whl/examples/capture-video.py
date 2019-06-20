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

#: Capturing video of a Stimulus animation (non-realtime animation)
"""
This demo demonstrates how the a rendered `Stimulus` animation can
be captured to a video file.  To do this, Shady must slow down
the animation below real time.

It requires the module `cv2` from the third-party package
`opencv-python`.
"""#.
if __name__ == '__main__':

	import Shady
	"""
	Parse command-line options:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( width=700, height=700, top=100, frame=True, canvas=True )
	
	gamma  = cmdline.Option( 'gamma',  -1,   type=( int, float ), min=-1, doc='This controls the World/canvas `.gamma` property describing the screen non-linearity (-1 means "sRGB").' )
	noise  = cmdline.Option( 'noise',  -0.2, type=( int, float, tuple, list ), min=-1.0, max=1.0, minlength=3, maxlength=3, doc='This controls the World/canvas `.noiseAmplitude` property. Supply a scalar to specify a gray luminance level, or an R,G,B triplet to specify a color. Negative values get you a uniform distribution, positive get you a Gaussian distribution.' )
	
	speed  = cmdline.Option( 'speed', 100,   type=( int, float ), container=None, doc='This controls the drift speed of the sinusoidal carrier wave in pixels per second.' )
	output = cmdline.Option( 'output', 'example_movie', type=str, minlength=1, container=None, doc='This is the filename (or file stem) for saving the video.' )
	
	cmdline.Help().Finalize()
	Shady.Require( 'cv2', 'numpy' ) # die with an informative error if either is missing
	
	"""
	Create a `World` and a `Stimulus`:
	"""#:
	world = Shady.World( **cmdline.opts )
	stim = world.Stimulus(
		signalFunction = Shady.SIGFUNC.SinewaveSignal,
		signalAmplitude = 0.5,
		plateauProportion = 0,
		cx = lambda t: t * speed,
		contrast = ( 0.5 + noise ) if noise < 0.0 else ( 0.5 - 3 * noise ),
		
		atmosphere = world
	)
	
	"""
	Capturing each rendered frame is itself a slow process, and
	will slow our animation down below real time. We are forced to
	choose between accurate timing of the animation as it appears
	in real time on screen, and accurate timing in the movie file.
	In this case, of course, we care about timing in the file.
	Since all Shady's animation routines are functions of time `t`,
	we can no longer pass the real wall time as `t`. Instead we
	must pass a "fake" clock output based on the nominal frame
	rate we want and the number of frames that have passed.
	
	This is done by setting the `world.fakeFrameRate` (which would
	normally be left as `None`): 
	"""#:
	
	world.fakeFrameRate = 60.0   # ensures accurate slower-than-real-time animation
	
	"""
	Now we make a `VideoRecording` instance.  We can pass it
	our `World` instance in the `fps` argument---this is a
	syntactic shorthand for passing `world.fakeFrameRate`.
	"""#:
	movie = Shady.VideoRecording( output, fps=world )

	"""
	To avoid corruption, the movie file will need to be
	explicitly closed. Let's ensure that happens, at the
	latest, when the `World` ends:
	"""#:
	world.BeforeClose( movie.Close )
	
	"""
	Now we need to set up an animation callback that calls
	`movie.WriteFrame` each time a new frame is rendered.
	We'll attach the animation callback to the `Stimulus`
	(though we could equally attach to the `World`).
	
	The `frame` argument to `.WriteFrame()` can be a
	`numpy` array,  or as a shorthand it can be a `World`
	or `Sitmulus` instance---anything with a `.Capture()`
	method that returns a numpy array; this method is
	then automatically called on each frame.
	"""#:
	@stim.AnimationCallback
	def StimFrame( self, t ):
		movie.WriteFrame( self )
	
	print( 'Now streaming output to ' + movie.filename )
	
	"""
	Note that the real-time animation has slowed down.
	The speed should be correct when the file is played
	back at 60 fps, however.
	
	Note that the default codec is lossy, so the 
	pixel values in the movie may not be 100% accurate
	(lossy movie files should not be used for analysis
	of stimulus content).
	
	Streaming will end when the `World` closes (which you
	can trigger with any key-press).
	"""#>
	@world.EventHandler
	def AnyKeyToExit( self, event ):
		if event.type == 'key_press': self.Close()
		
	""#>
	Shady.AutoFinish( world )

