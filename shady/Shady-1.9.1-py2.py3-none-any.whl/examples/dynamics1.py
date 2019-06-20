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

#: High-level tools for directing the action (procedural version) 
"""
This demo shows how to use the bundled Shady.Dynamics submodule
to easily create properties that evolve over time, and how to
glue different dynamics together with a state machine to switch
between different discrete groups of stimulus behaviors.

Most of the demo will walk you through the setup of the state
machine and its states, before running it at the end.

Note that this demo shows a procedural style of implementing
the logic of a state machine.  Its sister demo, dynamics2, shows
the contrasting object-oriented approach for doing the same thing.

"""#.
if __name__ == '__main__':

	"""
	Let's start by creating a World, configured according to
	whatever command-line arguments you supplied.
	"""#:
	import Shady
	from Shady.Dynamics import StateMachine, Integral, Transition
	
	cmdline = Shady.WorldConstructorCommandLine()
	cmdline.Help().Finalize()
	Shady.Require( 'numpy', 'Image' ) # die with an informative error if either is missing
		
	
	world = Shady.World( **cmdline.opts )
	
	"""
	We'll use our included example image, `alien1`, as a stimulus.
	Note that we're telling Shady to load all of the individual frame
	images from the `alien1` folder, not the `.gif` file.
	
	We'll start our alien at the left end the world.
	"""#:
	alien = world.Stimulus(
		Shady.PackagePath( 'examples/media/alien1/*.png' ),
		x = -world.width / 2,
	)
	
	"""
	Now we'll start constructing the pieces of our dynamic world.

	We want our alien to stand, run, jump, fall, in that order.
	He will also spiral out of control if you press a certain key.
	These states will be fairly simple: the running and spiraling
	states will be triggered by user key presses, and the will
	all run on timers (runnng will lead to jumping which will
	lead to falling, although a key-press will also speed up the
	jump).
	
	Shady's `StateMachine` class can handle all most of this
	automatically by stringing states together in a certain
	order, but if we want a state to have multiple possible
	next states, we'll need to define the logic ourselves,
	as we shall see.
	"""#:

	"""
	We'll start by defining the state machine, which we imported
	from the Shady.Dynamics module.
	"""#:
	sm = StateMachine()
	"""
	Let's add our five states one by one. We'll define what
	happens in each state later. Right now, we want to set up
	how the *changes* between states will work.
	
	First, we add the 'stand' state, already alluded to in
	the function above. We tell the state machine the name of
	the state, and also tell it which state (yet to be defined)
	will come after this state in the default ordering of the
	machine.
	"""#:
	sm.AddState( 'stand', next='run' )
	"""
	We will define 'run' next. Same thing, but we're also
	giving this state a duration in seconds before it
	automatically moves to the next state.
	"""#:
	sm.AddState( 'run',  duration=2, next='jump' )
	"""
	Same for 'jump' and 'fall'.
	"""#:
	sm.AddState( 'jump', duration=0.4, next='fall' )
	sm.AddState( 'fall', duration=1.0, next='stand' )
	
	"""
	For the 'spiral' state, instead of simply specifying
	the name of its subsequent state as a string literal,
	we'll define `next` as a *function* that outputs the
	name of the next state. The state machine will run
	this function, passing an instance representing the
	current state (whose name will be 'spiral') as its 
	argument. The function's output will determine
	the alien's fate at that time.
	
	The function checks how long the state has been
	running (`.elapsed`). If it's less than three
	seconds, the state machine will cancel the request
	to exit the state (built-in constant `CANCEL`).
	 
	Otherwise, it returns a string, which will be used as
	the name  for the next state. (If that state doesn't
	exist, an error will occur).
	
	"""#:
	def ExitSpiral( state ):
		if state.elapsed < 3:
			alien.frame = Transition( 0, 24, duration=0.1 ) # wiggle
			return StateMachine.CANCEL
		return 'stand'
		
	sm.AddState( 'spiral', next=ExitSpiral )
	
	"""
	We've defined the skeleton of our state machine,
	but none of the actual behavior associated with its
	states.
	
	We'll give our stimulus an animation callback, which
	is just a function that is called by Shady on every
	frame before drawing this stimulus. The animation
	callback takes the stimulus itself as its first argument
	and the stimulus time (by default: seconds since World
	creation) as as its second argument.
	"""#:
	
	"""
	Here is it
	"""#:
	@alien.AnimationCallback
	def RunningJump( self, t ):
				
		# Calling the StateMachine instance with time `t` is what actually causes
		# the state-transition logic and management to run. It returns an instance
		# of a `State` object:
		state = sm( t )
		
		# The `State` instance has an attribute `.fresh` which indicates whether
		# the current time `t` is the earliest time for the current state. It is
		# a handy way of implementing state onset behaviors procedurally.
		if state.fresh:
		
			# Now we'll just check which state we're in and change the alien
			# accordingly. State instances can be compared directly to strings
			# to check their names.
			if state == 'stand':
				self.xy = 0   # stop any dynamic attached to the .xy property
				self.Set( x=-world.width/2 + 100, y=0, frame=0 ) # re-position him
				
			# So far so static.  In the other states, we'll use more `Shady.Dynamics`
			# tricks---in particular, the `Integral` with respect to time.
			if state == 'run':
				self.Set( x=Integral( 400 ) + self.x, frame=Integral( 16 ) )
				
			# A double-integral of a constant will give us the constant acceleration
			# that you would get from gravity, in both the 'jump' and 'fall' states
			# (let's say gravitational acceleration is 5000 pixels per second per
			# second).  When he jumps, let's say our alien achieves an initial
			# upward velocity of 1500 pixels per second.
			if state == 'jump':
				self.Set(y=Integral(Integral(-5000) + 1500) + self.y, frame=0)				
			if state == 'fall':
				self.frame = Integral(160)  # heeeeeeelp
			
			# Finally we'll use non-linear transformations of an `Integral` to achieve
			# a faster-and-faster spiralling effect in the 'spiral' state:
			if state == 'spiral':
				radius = min( world.width, world.height ) / 2 - 100
				self.Set( x=-radius, y=0, frame=0 )  # stop any .x, .y and .frame dynamics
				self.xy = Integral( Integral( 0.1 ) ).Transform( Shady.Sinusoid, phase_deg=[ 270, 180 ] ) \
				        * ( radius - Integral( 20 ) ).Transform( max, 0 )
	
	"""
	Our alien will do things now, but we haven't yet implemented
	a way of getting him started, since there's no condition to
	terminate the first 'stand' state. We'll hook into Shady's
	`EventHandler` mechanism.
	
	Like the `AnimationCallback`, this can be done using a
	decorator on our function definition. The function should
	take two arguments: the `Shady.World` being hooked into
	(here, written as `self`) and the event that will be handled,
	which contains data about mouse and keyboard input.
	"""#:
	@world.EventHandler
	def KeyboardControl( self, event ):
	
		# Press space to start running, to jump, or to exit from a spiral:
		if event.type == 'text' and event.text == ' ':
			if sm.state in [ 'stand', 'run', 'spiral' ]:
				sm.ChangeState() # without args: change to the `.next` state
		
		# Press enter to start spiralling:
		if event.type == 'key_release' and event.key in [ 'enter', 'return' ]:
			sm.ChangeState( 'spiral' )  # change to this explicitly named state
				
		# Press q or escape to stop and close the window:
		if event.type == 'key_release' and event.key in [ 'q', 'escape' ]:
			self.Close()
	"""
	And that's it - the alien is away! Try using spacebar and
	enter key to manipulate his state.
	
	Remember that we designed `ExitSpiral` to ensure that you
	cannot get out of a spiral until you have been in it for
	at least 3 seconds.
	"""#>
	Shady.AutoFinish( world )
