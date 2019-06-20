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

#: High-level tools for directing the action (object-oriented version) 
"""
This demo shows a different way to create the interactive, dynamic
behavior seen in the `dynamics1`demo. We recommend that you go
through that demo first, because this demo assumes you're aware of
the behavior we're trying to achieve.

Rather than keeping the state objects very simple (just `duration`
and `next` attributes) and packing all of the logic into a big
procedural switch inside the Stimulus `Animate()` method, this
version of the same demo compartmentalizes the logic within each 
state itself. Each state has `onset`, `ongoing`, and `offset`
methods assigned to it that are respectively called when the state
begins, as the state progresses, and when the state ends.

As before, most of this demo is about walking you through the setup 
before running the final product at the end.
"""#.
if __name__ == '__main__':
	"""
	Let's start by creating a `World`, configured according to
	whatever command-line arguments you supplied, and creating
	our alien stimulus.
	"""#:
	
	import Shady
	from Shady.Dynamics import StateMachine, Integral, Transition
	
	cmdline = Shady.WorldConstructorCommandLine()
	cmdline.Help().Finalize()
	Shady.Require( 'numpy', 'Image' ) # die with an informative error if either is missing
	
	world = Shady.World( **cmdline.opts )
	
	"""
	While we're here showing alternative ways of doing the things
	we did before, we'll load the alien using the animated `.gif`
	file rather than its individual image frames:
	"""#:
	alien = world.Stimulus(
		Shady.PackagePath( 'examples/media/alien1.gif' ),
		x=-world.width / 2,
	)
	
	"""
	In `dynamics1`, we started off by defining `duration` and 
	`next` for each state as keyword arguments of the `AddState`
	method. This time, we'll fully define each state as a subclass
	of `StateMachine.State`, attach `.next`, `.duration`, etc
	as class attributes, and load the class definitions into the
	state machine as our final step.
		
	Our `Stand` state is fairly simple. We define the `next` 
	attribute.  All such attributes may be either constant,
	or callable with the `State` instance as sole argument.
	"""#:
	class Stand( StateMachine.State ):
		next = 'Run'

		"""
		Note that a callable class attribute that takes an instance
		of the class as its first argument is better known as... a
		method. So let's call it that. And define another method,
		called `onset`. This method does exactly what we previously
		accomplished by checking `state.fresh` in the procedural
		`dynamics1`: its code will be run once each time we enter
		the state.
		"""#:
		def onset( self ):
			alien.xy = 0  # stops any ongoing .xy dynamic
			alien.Set( x=-world.width / 2 + 100, y=0, frame=0 )
	"""
	Sometimes, as in the `onset` example here, your implementation
	of a `State` method might ignore the instance argument `self`.
	Your Python IDE may then give you a warning about this. You can
	suppress such warnings by putting the `@staticmethod` decorator
	above the method definition, if the warning bothers you more
	than this extra clutter does. Either way, functionality is the
	same.
	"""#:
			
	"""
	Our `Run` state is also similar to the 'run' section of the
	animation callback in `dynamics1`, but we've spiced things up a
	bit by making our alien walk with variable speed as a function
	of his gait cycle. We've also made the duration attribute a
	little longer than last time, to accommodate the funky gait.
	"""#:
	class Run( StateMachine.State ):
		duration = 3.5
		next = 'Jump'

		def onset( self ):
			gait = lambda t: 1 if alien.frame in [ 0, 12 ] else 10
			alien.Set(
				x=Integral( gait ) * 40 + alien.x,
				frame=Integral( gait ) * 3 + 1,
			)
			
	"""
	Nothing has changed in our 'Jump' state. (Note, though, that
	because we set `frame` to 0 for the jump, the alien's dynamic
	`gait` and hence his horizontal velocity automatically become
	constant.)
	"""#:
	class Jump( StateMachine.State ):
		duration = 0.4
		next = 'Fall'

		def onset( self ):
			alien.Set( y=Integral( Integral(-5000) + 1500 ) + alien.y, frame=0 )
	"""
	The 'Fall' state is a good place to demonstrate the `offset`
	method (called when the state machine *leaves* the state in
	question) and the `ongoing` method (which is called repeatedly
	while we're in the state, every time the state machine itself
	is called with a new time argument).
	"""#:
		
	import random
	class Fall( StateMachine.State ):
		duration = 3
		next = 'Stand'

		def onset( self ):
			alien.frame = Integral(160)

		"""
		The `ongoing` method offers an additional trick: you can return
		the name (or instance) of another state to immediately trigger
		a change to that state, as if you had called `sm.ChangeState(state)`.
		You can even return the name of the same state to restart it. If
		`ongoing` returns None (which happens if nothing is explicitly
		returned), nothing changes and the state continues. Here, we
		check the alien's altitude. If he falls below the bottom edge of
		the screen, we return the 'Stand' state. (The three-second duration
		is unlikely to be reached in this case, but we'll keep it anyway.)
		"""#:
		def ongoing( self ):
			if alien.y < -world.height / 2: return 'Stand'

		"""
		Typically, the `offset` method is best used to 'clean up' things
		that may have been affected by the departing state. This method
		will be called regardless of which state is coming up next, so
		it's not a good place to initialize what's coming next (use the
		next state's `onset` for that). Here, we'll assume that the
		alien falls through a wormwhole into a parallel `World` of
		a different (randomly-chosen) color.
		"""#:
		def offset(self):
			world.clearColor = [random.random(), random.random(), random.random()]
			
	"""
	Finally, we have our Spiral, which behaves the same as before.
	Note that, whereas before we defined an `ExitSpiral` function
	globally and passed it as the `next` argument to `AddState`, this
	time it is very natural to implement the same logic directly in
	`next` as a method:
	"""#:
	class Spiral( StateMachine.State ):

		def next( self ):
			if self.elapsed < 3:
				alien.frame = Transition( 0, 24, duration=0.1 ) # wiggle
				return StateMachine.CANCEL
			return 'Stand'

		def onset( self ):
			radius = min( world.size ) / 2 - 100
			alien.Set( x=-radius, y=0, frame=0 ) # stop any .x, .y and .frame dynamics
			alien.xy = Integral( Integral( 0.1 ) ).Transform( Shady.Sinusoid, phase_deg=[ 270, 180 ] ) \
			         * ( radius - Integral( 20 ) ).Transform( max, 0 )
	"""
	Now that we have our states, we can define the state machine
	and pass all of our states as constructor arguments. In the same
	line, we've set the alien's `.Animate` attribute to the state
	machine, which tells Shady that this alien should call the 
	state machine once every frame. This saves us the effort of writing:
	
		@alien.AnimationCallback
		def TediousAnimationDefinition( self, t ):
			sm( t )
			
	in order to attach the state machine to the alien.
	
	"""#:
	sm = alien.Animate = StateMachine( Stand, Run, Jump, Fall, Spiral )
	
	"""
	Sidebar: we took the explicit route to state machine construction
	there, but you could equivalently, if you find it more readable,
	construct an empty StateMachine first, and then call `sm.AddState()`
	with each of the states. The neatest way to do this is with a class
	decorator:

		sm = StateMachine()
		
		@sm.AddState
		def Stand( StateMachine.State ):
			...
			
	The decorator tells Shady to add the State subclass to the
	StateMachine immediately after it is defined.
	"""#:
	
	"""
	Finally, we'll create the same Event Handler we had in `dynamics1`.
	The only difference is that our state names are now capitalized,
	(because they're classes, and within Shady that is our convention
	for class names).
	"""#:
	@world.EventHandler
	def KeyboardControl( self, event ):
		if event.type == 'text' and event.text == ' ':
			if sm.state in [ 'Stand', 'Run', 'Spiral' ]:
				sm.ChangeState()
		elif event.type == 'key_release' and event.key in [ 'enter', 'return' ]:
			sm.ChangeState( 'Spiral' )
		elif event.type == 'key_release' and event.key in [ 'q', 'escape' ]:
			self.Close()
	
	"""
	All in all, there have been a few changes (some subtle, some not
	subtle) relative to the alien's previous adventure, but broadly the
	behavior is the same as in `dynamics1` despite the very different
	programming approach.
	"""#>
	Shady.AutoFinish( world )
