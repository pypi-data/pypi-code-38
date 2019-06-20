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

#: Property-sharing is a powerful tool for managing stimulus dynamics
"""
This demo shows how individual properties can be shared between different
Shady stimulus objects.

Often, you will want certain groups of `Shady.Stimulus` instances to
share one or more properties. The advantages of this are twofold.
Firstly, you save time, as you only need to adjust the properties of
one linked stimulus in order to affect all the stimuli linked to it.
Secondly, you save memory, as any shared properties among linked
stimuli will use the exact same value (or array of values).

Once shared, properties can be "un-shared" at any time and can have
their values adjusted individually.
"""#.
if __name__ == '__main__':
	"""
	Let's start by creating a World, configured according to
	whatever command-line arguments you supplied. We'll use the
	canvas by default, with a gamma of 2.2, so we test out some
	of the useful sharing techniques later on.
	"""#:
	import Shady
	cmdline = Shady.WorldConstructorCommandLine( canvas=True )
	cmdline.Help().Finalize()
	world = Shady.World( gamma=2.2, **cmdline.opts )

	"""
	Let's create some rectangles:
	"""#:
	a = world.Stimulus( size=[400,200], color=[1.0, 0.0, 0.0], bgalpha=0, x=-300, rotation=45 )
	b = world.Stimulus( size=[200,100], color=[0.0, 0.0, 1.0], bgalpha=0, x=+300 )
	c = world.Stimulus( size=[100, 50], color=[0.0, 0.7, 0.0], bgalpha=0, y=+300 )
	d = world.Stimulus( size=[100, 50], color=[0.7, 0.7, 0.0], bgalpha=0, y=-300 )
	
	"""
	Let's say `b` wants to be at the same angle as `a`.  Well, on
	one level that's trivial:
	"""#:
	b.rotation = a.rotation
	
	"""
	But when `a` moves on, `b` is left behind:
	"""#:
	a.rotation += 30
	
	"""
	Let's use a slightly different syntax:
	"""#:
	b.rotation = a  # what??
	"""
	That's right, it looked like we were trying to assign a
	Stimulus *instance* to a (usually numeric) property of
	another Stimulus---doesn't make much sense, right?
	But notice how the rectangles are aligned again? In fact,
	that was a syntactic shortcut for property sharing.
	The `.rotation` properties of `a` and `b` now share the
	same memory location.  A change to `a` will affect `b`:
	"""#:
	a.rotation = 0    # affects BOTH `a` and `b`
	
	"""
	...and (because they share the same memory) vice versa:
	"""#:
	b.rotation = 90   # ALSO affects both
	
	"""
	The power of this idea becomes clear when you want
	properties to be dynamic.  Let's attach a dynamic to the
	`.rotation` of `a`:
	"""#:
	a.rotation = lambda t: t * 45
	
	"""
	Now, a single piece of code is running on every frame,
	and dumping its result into the memory location of
	`a.rotation`. But since the memory location is now
	shared, that single piece of code can now simultaneously
	affect two stimuli (and could affect any number of
	stimuli) with no extra overhead cost.
	"""#:
	
	"""
	How do we make `b` independent again?  Using the same
	shorthand, we can tell `b` to "be itself" rather than
	trying to be somebody else:
	"""#:
	b.rotation = b
	# The instantaneous value of `b.rotation` does not
	# change, but it becomes unlinked from `a.rotation`.
	# And since `a`, not `b`, is the stimulus that has 
	# the dynamic `lambda` function running on it, `b`
	# stops rotating.
	
	"""
	The full verbose form of these operations is:
	"""#:
	b.LinkPropertiesWithMaster( a, 'rotation' )   # same as b.rotation = a
	# now they're spinning together again
	"""
	and...
	"""#:
	b.MakePropertiesIndependent( 'rotation' )   # same as b.rotation = b
	# now they're independent again
	
	"""
	Note the plural "Properties" in those method names:  one of the
	advantages of this more-verbose syntax is that you can link or
	unlink *multiple* properties in the same call.  Optionally, you
	can also *set* their values in the same breath, using keyword
	arguments:
	"""#:
	b.LinkPropertiesWithMaster( a, 'color', 'envelopeSize', plateauProportion=0 )
	# establish a link between `a` and `b` on all three properties:
	# .color,  .envelopeSize and .plateauProportion
	# At the same time, set plateauProportion=0 which will then
	# affect both stimuli.
	
	"""
	The same goes for declaring independence:
	"""#:
	b.MakePropertiesIndependent( 'plateauProportion', 'envelopeSize', color=[0,0,1] )
	# uncouple .plateauProportion and .envelopeSize but don't change their values;
	# uncouple .color and immediately change it back to blue
	
	"""
	There's a third method, `.ShareProperties()` that works from the
	perspective of the "master" Stimulus.  The main advantage to that
	is that you can propagate the sharing relationship to multiple
	*stimuli* in one call...
	"""#:
	a.ShareProperties( [ b, c, d ], 'rotation' )
	
	"""
	...as well as multiple properties. And again, it allows you the
	option of setting one or more properties explicitly at the same
	time, using keyword arguments:
	"""#:
	a.ShareProperties( b, c, d, 'envelopeSize', plateauProportion=1 )
	
	"""
	Note that only some attributes - specifically, fully-fledged
	`ManagedProperty` attributes, can be shared.  The `.x` attribute
	alone, for example, cannot be shared, because it is a
	`ManagedShortcut` to only a single element of the
	`.envelopeTranslation` array, and you are limited to being able
	to share property arrays entirely or not at all.  Try it yourself:
	I'm not going to do it, because that would crash the script,
	but you can try either or both of the following by typing them at
	the prompt::
	
	     c.x = a                        # wrong
	     a.ShareProperties( c, 'x' )    # equivalently wrong
	"""#:
	
	"""
	Also, you cannot share *unmanaged* properties like `.frame`
	or `.page` or `.text`.   Again, feel free to try it::
	
	     c.frame = a                        # wrong
	     a.ShareProperties( c, 'frame' )    # equivalently wrong
	"""#:
	
	"""
	To link a shortcut or unmanaged property, the best you
	can do is create a dynamic:
	"""#:
	
	c.x = lambda t: a.x
	# ... but of course that comes at an extra computational
	# cost, on each frame (small, in this case, but in complex
	# stimulus arrangements such costs can quickly add up)
	
	"""
	Anyway, now the two stimuli will automatically move together
	in just the x dimension: 
	"""#:
	a.xy = Shady.Transition(
		duration = 3,
		transform = lambda p: Shady.Sinusoid( 3.75 * p ) * 150 - 150,
	)

	"""
	There is, however, one 'virtual' managed property that
	exists principally to facilitate sharing.  It is a shorthand
	for a bundle of managed properties that affect linearization
	and dynamic range enhancement.
	
	Such things matter in visual psychophysics, so let's
	illustrate with a psychophysics-y stimulus:
	"""#:
	gabor = world.Stimulus(
		signalFunction = Shady.SIGFUNC.SinewaveSignal,
		signalAmplitude = 0.5,
		plateauProportion = 0.0,
	)
	# or, you know,  sigfunc=1, siga=0.5, pp=0
	# (depends where you like your code to reside on
	# the concise <-> readable spectrum)
	
	"""
	It's immediately, visibly obvious that we have failed to
	match the stimulus `.gamma` to that of the surrounding
	`World` and its canvas.  .gamma is one of the bundle of
	properties we're talking about, which we collectively
	call the `.atmosphere`:
	"""#:
	
	gabor.atmosphere = world
	# or equivalently:  gabor.LinkAtmosphereWithMaster( world )
	
	"""
	Now the whole set of properties is matched, and will
	track, the `World`. This becomes obvious if we take leave
	of our senses and start changing them in real time:
	"""#:
	
	world.ditheringDenominator = 3
	world.gamma = Shady.Oscillator( 1.0 ) * 0.5 + 2.2

	"""
	Seriously though, stop that:
	"""#:
	world.Set( ditheringDenominator=world.dacMax, gamma=2.2 )
		
	"""
	Side note: in fact, the `World` itself has no direct
	use for these properties: their visible effects are
	actually mediated by a `Stimulus` called "canvas". But
	the `World` has them, as placeholders. When a canvas
	is created (either by using the `canvas=True` constructor
	argument when creating the `World()`, or by a later
	explicit call to `world.MakeCanvas()`) these properties
	get shared between the `World` and its canvas, using
	exactly the kind of property-sharing mechanism we're
	learning about today. So then any change to these
	properties of the `World` will affect the canvas, and
	vice versa.
	
	You can learn more about the canvas and the "atmosphere"
	properties by looking at the `PreciseControlOfLuminance`
	topic documentation:
	"""#:
	
	help( Shady.Documentation.PreciseControlOfLuminance )
	# press Q to exit the help viewer
	
	"""
	The concept of a "master" is a fairly weak one, since any
	change to the property values is symmetric between master
	and followers.  Being the "master" means two things:
	
	1. when the sharing link is first made, the master's
	   current property values are preserved and the followers'
	   values are overwritten (unless the value is overridden
	   explicitly by a keyword argument in the method call,
	   as we saw above).
	"""#:
	"""
	2. depending on the rendering back-end you're using,
	   it may be meaningless for the "master" to declare
	   independence. But it is always meaningful for
	   the followers to declare independence.
	   (This is a difference between the `ShaDyLib` binary
	   accelerator and the pure-Python `PyEngine`. We may
	   try to iron this out in future, one way or the other,
	   but it's a low priority.)  Let's see what happens
	   there:
	"""#:
	
	a.MakePropertiesIndependent( 'rotation' )
	# If you're using the accelerator (ShaDyLib) for rendering,
	# nothing will happen - all colored blobs will keep rotating.
	# But if you have disabled the accelerator (for example, by
	# starting this script with --backend=pyglet --acceleration=False)
	# then `a` will break away and keep spinning while the others
	# will stop.
	
	"""
	Let's ensure things are back the way they were:
	"""#:
	a.ShareProperties( b, c, d, 'rotation' ) # all spinning again, if they weren't before
	
	"""
	Another unrelated potential gotcha is that you need 
	to remember how dynamic properties work: they install
	a small subroutine that is associated with the rendering
	of a *particular* Stimulus on each frame, and which dumps
	its results into the memory space of that Stimulus.
	This computation survives turning invisible:
	"""#:
	a.visible = 0
	"""
	...but not if that Stimulus leaves the stage entirely:
	"""#:
	a.Leave()   # all the others stop, because the dynamic
	            # was specific to the `a` stimulus
	"""
	They're still linked:
	"""#:
	b.rotation += 90   # all change
	"""
	...in both directions:
	"""#:
	a.rotation += 90  # all change again
	"""
	...but a dynamic...
	"""#:
	a.rotation = lambda t: t * 45
	"""
	...only runs when `a` is on-stage:
	"""#:
	a.Enter( visible=1 )
	
	"""
	Good luck sharing properties!
	"""#>
	Shady.AutoFinish( world )
