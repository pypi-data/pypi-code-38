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

#: Decoding and rendering of frames from a movie file or camera
"""
This demo script shows some of the things that can be done with
video stimuli.

By explicitly importing `Shady.Video`, you can enable the `.video`
property of the `Stimulus` class.   You can assign the filename of
a video file, or the integer ID of a live camera, to this property
(it is actually redirected to `.video.source`,  with `.video`
itself being an object that is implicitly constructed when needed).

Video file decoding and live camera acquisition both require the
`cv2` module from the third-party package`opencv-python`, which
can be installed via `pip`.

Be warned that video stimuli are fundamentally less efficient
than Shady's other more typical stimulus approaches: rather than
transferring everything to the graphics card up-front, or allowing
everything to be generated on-the-fly on the GPU, this uses
CPU code to decode every new frame from the video source and then
to transfer it from CPU to GPU.  Timing performance will likely
suffer as a result.
"""#.

import random

if __name__ == '__main__':

	import random
	import Shady

	"""
	Parse command-line options:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( width=1000, height=750 )
	source    = cmdline.Option( 'source',    Shady.PackagePath( 'examples/media/fish.mp4' ),  type=( int, str ), container=None, doc="Supply the path-/file-name of a movie file,  or an integer (starting at 0) to address a camera." )
	loop      = cmdline.Option( 'loop',      True,  type=bool, container=None, doc="Specifies whether or not to play the video on infinite loop." )
	transform = cmdline.Option( 'transform', False, type=bool, container=None, doc="Demonstrate ways to use, and not to use, the .video.Transform callback" )
	gauge     = cmdline.Option( 'gauge',     transform, type=bool, container=None, doc="Whether or not to show a `FrameIntervalGauge`." )
	multi     = cmdline.Option( 'multi',     0,     type=int,  container=None, doc="Specifies the number of animated copies of the video to make.  Copying and animation is efficient (happens all on GPU)." )
	cmdline.Help().Finalize()
	
	"""
	Enable video decoding by explicitly importing `Shady.Video`
	then create a `World`:
	"""#:
	import Shady.Video
	w = Shady.World( **cmdline.opts )
	if gauge: Shady.FrameIntervalGauge( w )
		
	"""
	Create a stimulus and set its `.video` property:
	"""#:
	s = w.Stimulus( video=source, bgalpha=0 )
	s.video.Play( loop=loop )

	""#>
	if transform:
		"""
		According to the command-line arguments, we've been asked
		to demonstrate the `.video.Transform()` mechanism. So, let's
		create a state machine.  We will rotate, in 3-second steps,
		between various options that will differently affect timing.
		"""#:
		sm = Shady.StateMachine()
		
		"""
		Some of the steps will use this helper function as the
		video transform:
		"""#:
		def Desaturated( x ):
			gray = x[ :, :, :3 ].mean( axis=2 )
			x[ :, :, 0 ] = gray
			x[ :, :, 1 ] = gray
			x[ :, :, 2 ] = gray
			return x
			
		"""
		In the first step, the video is not transformed.  Shady
		only transfers new data from CPU to GPU when a new image
		is supplied by the camera or decoded from the file. Note
		however, that even this will affect frame timing: Shady
		operates most smoothly when all possible image frames
		have been pre-loaded onto the GPU.
		"""#:
		@sm.AddState
		class DoNothing( Shady.StateMachine.State ):
			duration = 3
			next = 'TransformNewData'
			def onset( self ):
				s.video.Transform = None
			
		"""
		The next 3-second state demonstrates an efficient video-frame
		transformation: every time a *new* frame is decoded, transform
		it (in this case, desaturate it).  Not every display frame
		will entail a new frame of video content however, so if the
		video hasn't changed, return `None` to signal that nothing
		needs to be done.
		"""#:
		@sm.AddState
		class TransformNewData( Shady.StateMachine.State ):
			duration = 3
			next = 'ReturnOriginalEveryTime'
			def onset( self ):
				s.video.Transform = lambda x, changed: Desaturated( x ) if changed else None
			
		"""
		Add a 3-second state demonstrating an INEFFICIENT abuse of
		the transformation mechanism. The transformation is just the
		identity transform, so no change will be visible, but a
		"transformed" image is returned on every display frame. This
		means Shady will think it has to transfer a new texture to
		the GPU on every display frame, which ordinarily it would not
		do (normally it only needs to do this at the video frame rate,
		not the display frame rate).
		"""#:
		@sm.AddState
		class ReturnOriginalEveryTime( Shady.StateMachine.State ):
			duration = 3
			next = 'TransformEveryTime'
			def onset( self ):
				s.video.Transform = lambda x, changed: x
				
		"""
		Another example of what NOT to do: here we have the
		desaturating transformation implemented INEFFICIENTLY because
		it returns something on *every* display frame, regardless of
		whether or not there is new video content. 
		"""#:
		@sm.AddState
		class TransformEveryTime( Shady.StateMachine.State ):
			duration = 3
			next = 'DoNothing'
			def onset( self ):
				s.video.Transform = lambda x, changed: Desaturated( x )
		
		"""
		Ensure `sm( t )` is called on every frame:
		"""#:
		s.SetAnimationCallback( sm )

	"""
	The following function will be used if the --multi option was
	set >0.  It illustrates how you can use an existing `Stimulus`
	instance as the `source` of a new `Stimulus` during construction,
	causing the new `Stimulus` to share the old one's `.textureID`.
	"""#:
	def Spawn( multi ):
		s.plateauProportion = 1 # oval/circular
		s.video.aperture = min( s.video.aperture ) # definitely circular
		
		t0 = w.timeInSeconds # for synchronization (see below)
		for i in range( multi ):
			cyclical_offset = i / float( multi )
			cycle = Shady.Integral( 0.2 ) + cyclical_offset
			position = Shady.Apply( s.Place, cycle * 360, polar=True )
			anchor = Shady.Apply( Shady.Sinusoid, cycle, phase_deg=[ 270, 180 ] )
			# Each newly-created Integral starts its clock the first time it is called.
			# We'll call them once below, explicitly, with t0, before using them
			# as dynamic property values. This ensures that, even if each child stimulus
			# takes time to create, the dynamic properties are in synch across copies.
			# (This would be an issue in a threaded environment if you were to call
			# `Spawn(multi)` directly rather than `w.Defer( Spawn, multi )` because in
			# that case each `w.Stimulus()` call below would be deferred to the end of
			# the current frame, with the engine waiting synchronously for each one
			# to complete - so, it would take one frame per child).
			
			# create a new Stimulus that shares the old one's texture:
			child = w.Stimulus( s, position=position( t0 ), anchor=anchor( t0 ) )
			# copy all the physical properties of the parent Stimulus:
			child.Inherit( s )
			# actually share some of the properties (texture and texture dimensions):
			s.ShareTexture( 'envelopeSize', 'textureSize', child )
			# individually scale and animate the copy:
			child.Set( position=position, anchor=anchor, scaling=0.2 )
			child.color = [ random.random() for channel in 'rgb' ]
			
	if multi:
		w.Defer( Spawn, multi ) # use of .Defer() means that the explicit t0 synchronization, above, isn't actually required

	"""
	Set an event handler for keyboard control of the video:
	"""#:
	@w.EventHandler( -1 )
	def VideoKeyControl( self, event ):
		if event.abbrev in 'kp[ ]':
			s.video.playing = not s.video.playing
		if event.abbrev in 'kp[left] ka[left]' and not s.video.live:
			s.video.Pause()  # another syntax for setting s.video.playing = False
			if 'shift' in event.modifiers: s.video.frame = 0  # rewind to start
			else: s.video.frame -= 1  # step back
		if event.abbrev in 'kp[right] ka[right]' and not s.video.live:
			s.video.Pause()  # another syntax for setting s.video.playing = False
			if 'shift' in event.modifiers: s.video.frame = -1  # skip to end
			else: s.video.frame += 1  # step forward
	
	""#>
	print( """
                    space   pause/unpause
        left-/right-arrow   step back/forward one frame
shift + left-/right-arrow   rewind to first frame/skip ahead to last frame
""" )
	Shady.AutoFinish( w )

