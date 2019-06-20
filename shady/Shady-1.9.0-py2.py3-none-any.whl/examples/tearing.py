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

#: A quick visual test for "tearing" artifacts
"""
Tearing artifacts can arise when the windowing back-end fails to
synchronize with the display hardware (possibly because vertical
synchronization needs to be explicitly enabled in the control
panel of the driver for the graphics card).

This demo shows a `TearingTest()` stimulus which makes tearing
artifacts visible.  Watch out for this kind of effect::

            *****.....*****.....
            *****.....*****.....
            *****.....*****.....
                *****.....*****.....
                *****.....*****.....
                *****.....*****.....
                *****.....*****.....
                *****.....*****.....

as well as fast-moving arifacts that make the edges look "ragged"::

                *****.....*****.....
                /****.....*****..../
                /****.....*****..../
                *****.....*****.....
                /****.....*****..../
                *****.....*****.....
                *****.....*****.....
                /****.....*****..../

Blurry edges are OK; torn or ragged edges are not.  Bear in mind,
performance will probably be bad while the `World` is running in a
background window. Switch the window to the foreground before you
judge.

"""#.
if __name__ == '__main__':

	import Shady

	"""
	Parse command-line options:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine()
	ruler  = cmdline.Option( 'ruler', False, type=bool, container=None, doc='Whether or not to display a `PixelRuler` to verify screen resolution.' )
	gauge  = cmdline.Option( 'gauge', False, type=bool, container=None, doc='Whether or not to display a `FrameIntervalGauge` to help debug timing performance.' )
	period = cmdline.Option( 'period', 4.0, type=( int, float ), container=None, doc='Period, in seconds, of the oscillatory motion of the bar stimulus.' )
	swap   = cmdline.Option( 'swap',     1, type=( int ), container=None, doc='Number of physical frames per `World` update (NB: some back-ends and some operating systems may not support anything other than 1).' )
	cmdline.Help().Finalize()

	"""
	Create a `World` and, if requested, a frame interval gauge:
	"""#:
	world = Shady.World( **cmdline.opts )
	if gauge: gauge = Shady.FrameIntervalGauge( world )

	"""
	Configure the desired swap interval (according to the `--swap`
	command-line argument, if any) and also set up an event-handler
	to allow this to be changed on-the-fly by pressing number keys.
	"""#:
	
	@world.EventHandler( slot=-1 )
	def ChangeSwapInterval( self, event ):
		if event.type == 'key_press':
			Swap( self, event.key )
			
	def Swap( world, value ):
		try: value = int( value )
		except: return
		if value < 0: return
		print( '% 7.3f :  Attempting world.SetSwapInterval( %r )' % ( world.t, value ) )
		world.SetSwapInterval( value )
		
	if swap != 1: Swap( world, swap )
				
	"""
	Create the moving bar. Watch its edges.
	"""#:
	bar = Shady.TearingTest( world, period_sec=period ) #.Set( alpha=0.75 )
	
	""#>
	if ruler:
		"""
		Fill in the background with a `PixelRuler` pattern
		"""#:
		Shady.Require( 'numpy' ) # die with an informative error if this is missing
		ruler = Shady.PixelRuler( world )

	""#>
	print( 'Press Q or escape to close the window' )
	Shady.AutoFinish( world )
