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

#: Exploring the event-handling system
"""
This demo illustrates Shady's event-handling system.
"""#.
if __name__ == '__main__':
	"""
	Let's set up a `World`. By default we'll confine it to a small,
	out-of-the-way, draggable window.
	"""#:
	import Shady
	
	cmdline = Shady.WorldConstructorCommandLine(
		width=200, height=200, top=50, frame=True, fullScreenMode=False
	)
	cmdline.Help().Finalize()
	
	world = Shady.World( **cmdline.opts )

	"""
	And we'll put a white circle in the middle of it, because
	why not:
	"""#:
	circle = world.Stimulus( size=[150,150], pp=1, bgalpha=0, color=1 )
	
	"""
	Every time a keyboard, mouse, or other relevant windowing-system
	event occurs, an object representing that event is passed through
	a cascade of the `World`'s event-handler functions.  Each handler
	is associated with a numeric "slot" number, and the handlers are
	called in increasing slot order.  If a handler returns any kind of
	truthy value after processing a particular event, the cascade is
	aborted for that particular event.
	
	By default, a `World` has one handler, in slot 0, and that is its
	`HandleEvent` method (so you can overshadow this if you make a
	`World` subclass---then you don't have to do anything else).
	
	Event handlers can be removed or replaced using the
	`.SetEventHandler` method, or the `.EventHandler` decorator.
	All event handlers must take two arguments: `( world, event )`.
	
	The default implementation of `HandleEvent` is along the following
	lines:
	"""#:
	
	@world.EventHandler     #   equivalent to @world.EventHandler(slot=0)
	def HandleEvent( self, event ):
		if event.type == 'key_release' and event.key in [ 'q', 'escape' ]:
			self.Close()
	
	"""
	As a simple illustration, we'll implement an additional handler, in
	slot -1 so that it runs just *before* the one above that implemented
	q-or-escape-to-close.
	
	This one will establish a kind of mouse cursor inside the window.
	It changes color according to whether you're inside or outside the
	white circle. If you hold down shift as you move, it will stay
	inside the circle.
	"""#:
	
	dot = world.Stimulus( color=[1,0,0], bgalpha=0, pp=1, visible=0, size=20 )
	
	@world.EventHandler( slot=-1 )
	def MoveDot( self, event ):
		if event.type != 'mouse_motion': return

		relX, relY = Shady.RelativeLocation( [ event.x, event.y ], circle, normalized=True )
		# converts from World-centric to Stimulus-centric coordinates (in this case, normalized)
		normalizedRadialDistance = ( relX ** 2 + relY ** 2 ) ** 0.5
		dot.Set( visible=True, x=event.x, y=event.y, color=[ 1, 0, 0 ] )
		if normalizedRadialDistance > 1.0:
			if 'shift' in event.modifiers.split():
				dot.xy = circle.Place( relX / normalizedRadialDistance, relY / normalizedRadialDistance )
				# the .Place method converts from normalized Stimulus-centric coordinates
				# to World-centric pixel coordinates
				# TODO: this 'shift' behavior is never triggered in the pyglet back-end
			else:
				dot.color = [ 0, 1, 1 ]

	"""
	As should be clear from the two examples above, details of
	various types of keyboard, mouse or window event are encoded
	in attributes of the `event` instance. The names of the attributes
	are the same across different windowing back-ends. The values
	are largely similar too, although there are a few minor
	differences between back-ends.  There are also a few small
	back-end-specific differences in the range of event types that
	can be delivered and the order in which they are delivered.
	"""#.
	
	# This will be hidden during the demo, but it's as good a place
	# as any to keep a record of the differences I've observed so far.
	"""
	Examples:
	
	* ShaDyLib issues the first event of type 'text' after the
	  corresponding event of type 'key_press', whereas pyglet issues
	  the first 'text' event *before* the corresponding 'key_press'.
	* ShaDyLib records the .modifiers that were held down with
	  all mouse events; pyglet records them for mouse press and
	  release events, but not 'mouse_motion'.
	* A press or release of the spacebar can be identified under
	  ShaDyLib using `event.key==' '` whereas under pyglet it would
	  be `event.key=='space'`
	* ShaDyLib refers to Mac's "command" key as 'super' whereas
	  pyglet refers to it as 'command'.
	* ShaDyLib issues events of type 'mouse_enter', 'mouse_leave',
	  'window_focus', 'window_unfocus' and 'window_close' whereas
	  our pyglet-based back-end does not.
	* ShaDyLib does not issue an event of type 'text' when you
	  press the 'enter' key; pyglet does.
	"""

	
	"""
	The event.x and event.y coordinates are expressed relative
	to the `World`'s origin or "anchor" position. Let's add
	yet another event-handler, to allow you to play with that. It
	lets you toggle the anchor by pressing the spacebar.  After
	toggling, keep moving the mouse, and observe how the x and y
	coordinate frame has changed.
	
	Note that our red-dot handler does not need to be updated to
	accommodate the change of coordinate system. So the effects
	on the coordinate system will not be immediately obvious to
	you. However, soon we will be filling your console with
	event information and then it will make more sense.
	
	"""#:
	world.possibleAnchors = [ [ j, i ] for i in [ -1, 0, +1 ] for j in [ -1, 0, +1 ] ]
	@world.EventHandler( slot=-2 )
	def ToggleWorldOrigin( self, event ):
		if event.type == 'key_press' and event.key in [ ' ', 'space' ]:
			newAnchor = world.possibleAnchors.pop( 0 )
			world.possibleAnchors.append( newAnchor )
			world.anchor = newAnchor
			msg = '    changed anchor to %r    ' % newAnchor
			print( '\n%s\n%s\n%s' % ( '*' * len( msg ), msg, '*' * len( msg ) ) )

	""#.
	try: _SHADY_CONSOLE_INTERACT
	except NameError: pass
	else:
		"""
		If you ever want to remove a handler from a particular slot,
		you just set the handler to `None` in that slot:
		"""#:
		world.SetEventHandler( None, slot=0 )   # removes our q-or-escape-to-close handler

	"""
	In the end, the best way to learn about any event system is
	to observe empirically what happens. We'll set up yet another
	handler, in slot -3 so that it runs before the others. All
	the new handler really does is print the event instance, but
	we'll add a few bells and whistles. 
	"""#:
	
	world.printEvents = True
	world.previousEvent = None
	@world.EventHandler( slot=-3 )
	def PrintEvent( self, thisEvent ):
		# Let's allow the flood of console information to be turned
		# on or off by pressing P
		if thisEvent >> "kp[p]": # syntactic shorthand---see below
			self.printEvents = not self.printEvents
		elif not self.printEvents:
			return
			
		# OK, so we're printing. Let's add some context-sensitive 
		# blank lines to make the output easier to read:
		if self.previousEvent is not None and self.previousEvent.type != thisEvent.type:
			if self.previousEvent.type in [ 'mouse_motion', 'key_release' ]: print( '' )
			elif thisEvent.type in [ 'mouse_motion', 'key_press' ]: print( '' )
		self.previousEvent = thisEvent
		
		# Let's report the frame number as well
		thisEvent.frame = self.framesCompleted
		
		# Main payload:
		print( thisEvent )

	"""
	Now you can manipulate the mouse and keyboard, and observe what
	happens in the event stream (NB: keyboard events are only
	registered when the Shady stimulus window is in the foregound).
	Here are some final notes before the console gets flooded with
	event information:
	
	Those extra blank lines will generally group sets of related
	keyboard and mouse events together, but they are slightly
	misleading in the particular case of touch-screen taps, which
	generate tight clusters of consecutive `mouse_motion`,
	`mouse_press` and `mouse_release` events.

	Note also the shorthand syntax we used above in the last
	handler, `thisEvent >> "kp[p]"`.  You'll see from the console
	output below that each event has a field called `.abbrev`, which
	contains an abbreviated form of the event's `.type` and, where
	appropriate, its `.key`, `.text` or `.button` content. The
	syntax `e >> s` is equivalent to `e.abbrev in s`. This allows
	for easier programming of event tests.
	
	OK, that's all. Try it out...:
	"""#>

Shady.AutoFinish( world )
