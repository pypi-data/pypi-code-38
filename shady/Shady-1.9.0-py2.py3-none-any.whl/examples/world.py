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

#: Creates a `World`, starts a shell and leaves the rest to you.
"""
This script presents an interactive tabula rasa: it creates a
`World` instance called `w`, configured according to the command-line
options you supply, starts an interactive shell, and then leaves
you to it.
"""#.

if __name__ == '__main__':
	import Shady
	
	"""
	Parse command-line options that affect `World` construction:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( fullScreenMode=False, reportVersions=True )
	gamma = cmdline.Option( 'gamma', 1.0,   type=( int, float, str ), strings=[ 'sRGB' ] )
	bg    = cmdline.Option( 'bg',    0.5,   type=( int, float ) )
	gauge = cmdline.Option( 'gauge', False, type=bool, container=None )
	grid  = cmdline.Option( 'grid',  False, type=( bool, str ), strings=[ 'centered' ], container=None )
	cmdline.Help().Finalize()
	
	"""
	Create a `World` and report some version information:
	"""#:
	w = Shady.World( **cmdline.opts )
	
	"""
	Optional extras:
	"""#:
	if gauge: f = Shady.FrameIntervalGauge( w, corner=Shady.LOWER_LEFT )
	if grid:
		numpy = Shady.DependencyManagement.Import( 'numpy' )
		if numpy:
			p = Shady.PixelRuler( w )
			if grid == 'centered': p.carrierTranslation = w.size / 2
		else:
			print( '\ncould not create a PixelRuler (%s)\n' % numpy )
	"""
	Okay, over to you. Bye.
	"""#>
	Shady.AutoFinish( w, shell=True )
