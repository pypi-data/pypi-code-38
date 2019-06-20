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

#: How to switch between frames of a multi-frame image
"""
This file demonstrates two different ways of switching
between frames of a multi-frame image.

This demo requires third-party packages `numpy` and
`pillow`.
"""#.
if __name__ == '__main__':

	"""
	First deal with the demo's command-line arguments,
	if any:
	"""#:
	import Shady
	cmdline = Shady.WorldConstructorCommandLine()
	cmdline.Help().Finalize()
	Shady.Require( 'numpy', 'Image' ) # die with an informative error if either is missing
	
	"""
	Create a World:
	"""#:
	w = Shady.World( **cmdline.opts )
	
	"""
	Now we'll create an inhabitant.
	"""#:
	filename = Shady.PackagePath( 'examples/media/alien1.gif' )
	s = w.Stimulus( filename )

	"""
	Now we'll make him walk, by setting his `.frame`
	property to a function of time:
	"""#:
	s.frame = lambda t: t * 16

	"""
	The `.frame` property, like many World and Stimulus
	properties, supports dynamics.  That means that,
	instead of setting it to a constant numeric value,
	you can assign a function of time.
	
	If you ask to retrieve `s.frame`....
	"""#:
	print( s.frame )
	
	"""
	...then you get the instantaneous numeric value of
	the property. If we do it repeatedly, we will get
	different values:
	"""#:
	print( s.frame )
	import time;  time.sleep(0.5)
	print( s.frame )

	"""
	Stimuli can be created in this way from animated GIFs
	(or equivalently from lists of pixel arrays, each array
	specifying one frame). What actually happens is that the
	frames are concatenated horizontally to form one wide
	strip in the "carrier" texture:
	"""#:
	s.frame = 0
	s.scaling = Shady.Transition( s.scaling, w.width / float( s.textureSize[0] ) )
	s.WaitFor( 'scaling' )
	s.width = Shady.Transition( s.width, s.textureSize[0] )
	# now we're looking at the whole strip

	"""
	Normally, the first element of `s.envelopeSize` (a.k.a `s.width`)
	is set so that only one frame is visible.  A change of `s.frame`
	is actually realized by changing `s.carrierTranslation[0]` (a.k.a.
	`s.cx`), so the carrier moves one frame-width at a time under the
	envelope, like a zoetrope.
	
	Well that's all very nice, and it only uses one OpenGL texture,
	but there's a limit to the dimensions that an OpenGL texture can
	have.  So if the frame width multiplied by the number of frames
	were to exceed the limit (which is hardware-/driver-defined, but
	I've seen it be as low as 8192 pixels) then you will not be able to
	do things this way.  So there is a different animation mechanism,
	called the "page" mechanism, if you need it...
	"""#:
	
	"""
	First let's put our friend back the way he was:
	"""#:
	s.Set(
		frame = lambda t: t * 16,
		scaling = Shady.Transition( s.scaling, 1.0 ),
		width = Shady.Transition( s.width, s.frameWidth ),
	)
	
	"""
	Now let's load the frames from disk into RAM:
	"""#:
	frames = Shady.LoadImage( filename )
	
	"""
	It's a list of PIL Image objects. Type `frames` and press
	return if you don't believe me.  Go ahead, I'll wait.
	"""#:
	
	"""
	Now we'll create a new empty Stimulus:
	"""#:
	s2 = w.Stimulus( x=300 )
	
	"""
	It currently has no texture, and its .backgroundColor is set
	to the default mid-grey.  Let's load each frame of the image
	into a new "page".  A new page corresponds to a new allocated
	texture in OpenGL, and its associated dimension settings:
	"""#:
	for i, frame in enumerate( frames ):
		s2.NewPage( frame, key=i )
	
	"""
	You may have noticed that we could see the textures being
	loaded one by one. In practice you might want to create the
	Stimulus with `visible=False` and only make it visible after
	all the textures are in place. Alternatively, you can
	automate the process in one call:
	"""#:
	
	s2.LoadPages( frames )
	# you can also construct the Stimulus with the option `multipage=True`
	
	"""
	Either way, now we can use the `.page` property, which also
	supports dynamics in the same way as `.frame`. This time, for
	fun, let's use a special callable object from the `Shady.Dynamics`
	sub-module:
	"""#:
	s2.page = Shady.Integral(16)
	
	"""
	Are they marching out of step with each other?  They may or
	may not be, depending on exactly when you executed that last
	line, because the newly-constructed `Integral()` would have
	started from zero on the next frame after that.  If it bothers
	you, I can think of a few different ways of putting these two
	guys into lock-step. The first is to retrieve the instantaneous
	numeric value of `s.frame` and add it to a new `Integral()`: 
	"""#:
	s2.page = Shady.Integral(16) + s.frame
	
	"""
	That at least demonstrates how you can do arithmetic operations
	with `Shady.Function` objects.  But this approach is overkill
	when you could instead assign to `s2.page` a simple function of
	time that always returns the current value of `s.frame`:
	"""#:
	s2.page = lambda t: s.frame
	
	"""
	Note that, while `.page` and `.frame` support dynamic value
	assignment, they are not fully-fledged "managed properties".
	Often, you will want to share properties between stimuli,
	and can take advantage of "property sharing" which allows
	this kind of linkage *without* requiring additional Python
	instructions to run on each frame. The `sharing` demo has
	more details.  However, for indirect "unmanaged" properties
	like `.page` and `.frame`, adding a lambda function that
	executes on each frame is about the best we can do to
	synchronize them.
	"""#:
	
	"""
	You can even combine the `.page` and `.frame` concepts to
	select between different animations for the same stimulus.
	
	To illustrate this, let's gather some resources created
	by craftpix.net and released under the OpenGameArt.org
	license. Let's use a `glob` pattern to see what we've got:
	"""#:
	import os, glob
	patterns = {
		os.path.basename( d ) : d + '/*.png'
		for d in glob.glob( Shady.PackagePath( 'examples/media/alien2/*' ) )
		if os.path.isdir( d )
	}
	for key, pattern in sorted( patterns.items() ):
		print( '% 6s :  %s' % ( key, pattern ) )
	
	
	"""
	Now let's create a single stimulus that can switch between
	these collections of frames:
	"""#:
	alien2 = w.Stimulus( x=-300, frame=Shady.Integral( 5 ) )
	for key, pattern in sorted( patterns.items() ):
		alien2.NewPage( pattern, key=key )
		print( 'loaded %r' % key )
		
	"""
	Now we can switch between them:
	"""#:
	alien2.page = 'fire'
	
	"""
	We can address the pages by those string names we gave
	them, or numerically. The latter means we could even
	cycle through the different animations automatically: 
	"""#:
	alien2.page = Shady.Integral( 0.3 )
	
	""#>
	Shady.AutoFinish( w ) # tidy up, in case we're not running this with `python -m Shady`