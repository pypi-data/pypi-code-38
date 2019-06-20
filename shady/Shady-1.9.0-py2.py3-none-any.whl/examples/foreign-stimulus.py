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

#: How to add "foreign" (non-Shady) stimuli to a World
"""
Shady lets you draw anything you like among its stimuli.
This script demonstrates how you can write a custom class,
for use as a "foreign" (non-Shady) stimulus. The only thing
it needs is a `.Draw()` method that takes no additional
arguments.  You are free to use any OpenGL drawing commands
you want in this method (the only caveat being that,
depending on whether you are using "legacy" or "modern"
OpenGL commands, you should ensure that the `World` is created
with `legacy=True` or `legacy=False` appropriately).  The
current demo uses certain Shady features as helpers---
specifically the `World` projection matrix, and an `Integral`
instance---but in principle there is no need to refer to Shady:
you can do whatever you want.

This demo requires third-party modules `OpenGL` (from the
package `PyOpenGL`) and `numpy` (from `numpy`).
"""#.

import random

if __name__ == '__main__':
	import Shady
	Shady.DependencyManagement.Define( 'OpenGL', packageName='pyopengl' )

	"""
	First deal with the demo's command-line arguments, if any.
	Note that we're setting `legacy=True` to ensure that a
	legacy OpenGL context is created (or at least legacy-
	compatible one) because later we will be using old-fashioned
	legacy OpenGL commands.
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( legacy=True )
	cmdline.Help().Finalize()
	Shady.Require( 'OpenGL', 'numpy' ) # die with an informative error if either is missing
	
	"""
	Create a World:
	"""#:
	w = Shady.World( **cmdline.opts )
	w.perspectiveCameraAngle = 120 # default is 0, which means orthographic
	                                 
	"""
	Let's define a Shady stimulus for our foreign stimulus to
	interact with. Normally the `PixelRuler()` stimulus is
	created at a positive depth to ensure it lies behind most
	other stimuli, but here we'll explicitly reset its `.z` to 0
	(the default for most stimuli). Shady's convention for
	perspective projections is that stimuli at `z=0` are  pixel-
	for-pixel; at closer and further depths, pixels will start
	to get interpolated.
	"""#:
	
	grid = Shady.PixelRuler( w ).Set( z=0, carrierTranslation=w.size / 2 )
	
	
	"""
	Import OpenGL command bindings, from the third-party `PyOpenGL`
	package. (NB: you could use `pyglet.gl` here instead of
	`OpenGL.GL`, but pyglet does not wrap any of the gl* functions,
	which means some of them are less easy-to-use: for example you
	would have to wrap sequences by hand in `ctypes` containers---
	it's easier just to install PyOpenGL).
	"""#:
	
	from OpenGL.GL import *
	
	"""
	Now we'll define a custom stimulus class. From Shady's point of
	view the only requirement is that it should have a method called
	`.Draw()` or `.draw()`, taking no arguments. There is no need
	for the class to contain any reference to Shady classes or
	functions---you can work entirely in OpenGL.
	"""#.
	
	""#:

	class CustomStimulus( object ):
		def __init__( self ):
			self.vertexColors = {}
			self.last_normal = None
			self.boring = False
			
			self.angular_velocities = [ 23, 31, 37 ]
			self.rotation = Shady.Integral( lambda t: self.angular_velocities )
			
			glEnable( GL_LIGHTING )
			glEnable( GL_LIGHT0 )
			
		def Normal( self, x, y, z ):
			"""
			Define a normal vector (in legacy-OpenGL "direct mode"),
			and remember it (for the purpose of recalling which color
			belongs to which face, when `.boring` is set to `True`).
			"""
			glNormal3f( x, y, z )
			self.last_normal = ( x, y, z )
		
		def Vertex( self, x, y, z ):
			"""
			Draw a vertex (in legacy-OpenGL "direct mode") and choose a
			color for it if not already chosen.
			"""
			if self.boring: key = self.last_normal # different solid color on each face
			else:           key = ( x, y, z )      # different color at each vertex
			color = self.vertexColors.get( key, None )
			if color is None: color = self.vertexColors[ key ] = self.NewColor()
			glColor4f( *color ) # only respected if lighting is disabled
			glMaterialfv( GL_FRONT, GL_AMBIENT, color ) # only respected if lighting is enabled
			glMaterialfv( GL_FRONT, GL_DIFFUSE, color ) # only respected if lighting is enabled
			glVertex3f( x, y, z )
			
		def NewColor( self ):
			color = [ random.random() for channel in 'rgb']
			if len( color ) < 4: color.append( 1.0 )
			return color
		
		def Draw( self ):
		
			# In this demo we'll use the GL_PROJECTION and GL_MODELVIEW matrix
			# stacks, which are part of OpenGL's "fixed function pipeline", which
			# is a deprecated ("legacy") OpenGL feature.
			
			# (1) Projection
			glMatrixMode( GL_PROJECTION )
			glPushMatrix()
			
			# Get the matrix product of w.matrixWorldNormalizer
			# and w.matrixWorldProjection (NB: requires numpy):
			m = w.projectionMatrix
			# In the orthographic case, the z clipping planes are at z=-1 and z=+1.
			# So let's change the z-scaling to give ourselves some room (+/- 0.5*width):
			if 0.99 < m[ 2, 2 ] < 1.01:
				m[ 2, 2 ] = 2.0 / w.width
			# Transfer the projection matrix:
			glLoadMatrixf( list( m.T.flat ) )
			
			# (2) Scene composition
			glMatrixMode( GL_MODELVIEW )
			glPushMatrix()												
			
			glLightfv( GL_LIGHT0,   GL_POSITION, [ -1.0, +1.0, -1.0, 0.0 ] )
			glLightfv( GL_LIGHT0,   GL_AMBIENT,  [ 0.5, 0.5, 0.5, 1.0 ] )
			glLightfv( GL_LIGHT0,   GL_DIFFUSE,  [ 1.0, 1.0, 1.0, 1.0 ] )
			
			# Foreign stimuli don't have dynamic properties (they have no features
			# at all, beyond what we decide to define here in this class) but let's
			# make a poor-man's version here, to allow z to be dynamic:
			z = self.z
			if callable( z ): z = z( w.t )
			# fixed-function-pipeline transformations:
			glTranslatef( 0, 0, z ) # translation to the desired z coordinate
			
			omega, phi, kappa = self.rotation( w.t )
			glRotatef( omega, 1, 0, 0 ) # rotation about x axis as a function of time
			glRotatef( phi,   0, 1, 0 ) # rotation about y axis as a function of time
			glRotatef( kappa, 0, 0, 1 ) # rotation about z axis as a function of time
			
			r = 100 # half the length of one side of the cube, in pixels
			N = self.Normal
			V = self.Vertex
			glBegin( GL_QUADS ) # this is "direct-mode" drawing (also a legacy feature)
			N(-1, 0, 0); V(-r,-r,-r); V(-r,-r,+r); V(-r,+r,+r); V(-r,+r,-r) # left
			N(+1, 0, 0); V(+r,+r,-r); V(+r,+r,+r); V(+r,-r,+r); V(+r,-r,-r) # right
			N( 0,-1, 0); V(-r,-r,-r); V(+r,-r,-r); V(+r,-r,+r); V(-r,-r,+r) # bottom
			N( 0,+1, 0); V(-r,+r,+r); V(+r,+r,+r); V(+r,+r,-r); V(-r,+r,-r) # top
			N( 0, 0,-1); V(-r,+r,-r); V(-r,-r,-r); V(+r,-r,-r); V(+r,+r,-r) # near
			N( 0, 0,+1); V(-r,+r,+r); V(-r,-r,+r); V(+r,-r,+r); V(+r,+r,+r) # far
			glEnd()
			
			glPopMatrix() # finished with GL_MODELVIEW matrix stack
			glMatrixMode( GL_PROJECTION )
			glPopMatrix() # finished with GL_PROJECTION matrix stack
			
	"""
	Now that it's defined, we'll add it to the World.  We'll give it
	the actual class object, rather than an instance of that class.
	When the method `.AddForeignStimulus()` receives a callable object,
	it calls it to obtain an instance. This is an easy way of ensuring
	that all those OpenGL calls are "deferred" into the correct thread
	where necessary:
	"""#:
	
	c = w.AddForeignStimulus( CustomStimulus, z=-100 )
	
	"""
	It doesn't look quite right, does it? Let's turn OpenGL's depth
	test on, to ensure that the occluded parts of the surfaces are not
	drawn:
	"""#:
	
	w.Culling( True )

	""#>
	@w.EventHandler( slot=-1 )
	def Keys( self, event ):
		if event >> "kp[p]": # toggle perspective/orthographic projection
			self.perspectiveCameraAngle = 0 if self.perspectiveCameraAngle else 120
		if event >> "kp[g]": # toggle pixel grid on/off (at z=0)
			grid.visible = not grid.visible
		if event >> "kp[z]": # toggle depth oscillation on/off
			c.z = 0 if callable( c.z ) else Shady.Oscillator( 0.3 ) * 100
		if event >> "kp[l]": # toggle lighting on/off
			if glIsEnabled( GL_LIGHTING ): glDisable( GL_LIGHTING )
			else: glEnable( GL_LIGHTING )
		if event >> "kp[c]": # re-randomize colors (with shift to change mode)
			c.vertexColors.clear()
			if 'shift' in event.modifiers: c.boring = not c.boring
		if event >> "kp[d]": # toggle depth test on/off
			if glIsEnabled( GL_DEPTH_TEST ): w.Culling( False )
			else: w.Culling( True )
		if event >> "kp[ ] kp[s]": # pause/unpause spin
			if all( x==0 for x in c.angular_velocities ):
				c.angular_velocities = [ 23, 31, 37 ]
			else:
				c.angular_velocities = [  0,  0,  0 ]
			
	""#>
	print("""
  P    toggle perspective/orthographic projection

  G    toggle pixel-grid on/off at z=0

  Z    toggle z-oscillation on/off (note how the cube
       interacts with the pixel-grid Stimulus)

  S    pause/unpause the spin

  L    toggle lighting effect on/off

  C    re-randomize colors (press shift to switch
       between two different coloring strategies)

  D    toggle depth test on/off
""")
	
	""#>
	Shady.AutoFinish( w ) # tidy up, in case we're not running this with `python -m Shady`
