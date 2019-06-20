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

"""
On its own, `python -m Shady` starts an interactive prompt, in a subsidiary
thread, with the `Shady` package already imported and in which any construction
and running of a `Shady.World` will be redirected to the main thread. This is
part of the functionality of the `run` subcommand, which is assumed by default.
More generally,
::

	python -m Shady SUBCOMMAND [...]

can be used to invoke one of the following behaviors according to the
specified `SUBCOMMAND`:

`demo`

	The syntax::
	
		python -m Shady demo SCRIPT_NAME [...]
	
	starts a subsidiary thread, which will either interpret the specified
	script, or start an interactive prompt if `SCRIPT_NAME` is omitted.
	Construction and running of a `Shady.World` in that script/session
	will be redirected to the main thread.  This allows Shady to be
	tested or interactively explored in a multi-threaded environment,
	even on platforms that would not allow the `Shady.World` to run in
	a subsidiary thread (see `Shady.Documentation.Concurrency` for more
	details).

	The interpreter will stop and print a preview of each annotated section
	of code , and allow input from an interactive prompt. By default, the
	third-party package `IPython` is used to implement the prompt, if it
	is available. You can explicitly force the use of a vanilla (non-
	IPython) prompt if you add the option `--console=Python` on the command
	line. Or you can disable previewing and interaction completely by saying
	`--console=None` (this makes the `demo` subcommand identical to the
	`run` subcommand).

	If `SCRIPT_NAME` does not directly indicate an existing file, but the
	`examples/` subdirectory of the Shady package directory contains a
	script of the specified name (plus the `.py` extension if `SCRIPT_NAME`
	does not already have it) then the corresponding example script will
	be run.  This means you can say, for example::

		python -m Shady demo showcase

	and the script  `<path-to-Shady>/examples/showcase.py` will be used.

	Additional command-line options are interpreted by the specified script
	itself.  For example, most of the bundled example scripts respond to
	the `--help` option which will cause them to list their other options.


`run`

	This is the same as the `demo` subcommand except that the `--console`
	option will default to `None` for script handling. If no `SCRIPT_NAME`
	is supplied, an interactive prompt will be opened in a subsidiary
	thread.  If `SCRIPT_NAME` is specified, a subsidiary thread will be
	used to interpret the script (looking in the Shady package's
	`examples/` subdirectory to match the filename if not otherwise found)
	but with no previewing and no prompt.  In either case, construction
	and running of a `Shady.World` will be redirected to the main thread.
	
	The `run` subcommand is assumed by default, so the following are
	equivalent to each other:

		python -m Shady showcase
		python -m Shady run showcase

	and by the same token, `python -m Shady` is the same as
	`python -m Shady run`.

	Note: if Shady opens a full-screen window blocking your console,
	you should still be able to alt-tab (or command-tab) away. Timing
	performance will likely be poorer while the Shady window is in the
	background.  Also, unless the default event-handling behavior is
	overridden, Shady windows can be closed and the engine terminated
	by pressing either the `q` or the `escape` key.

	
`list`

	Lists the names of the available example scripts.
	
	
`screens`

	Lists details of the available display devices.
	
	
`timings`

	The syntax::

		python -m Shady timings LOG_FILE_NAME

	uses `Shady.PlotTimings` to plot a timing analysis based on the
	specified log file (created by passing the `logfile` option to some
	previous `World`'s constructor).
	
	
`help`

	`python -m Shady help`  displays the documentation you are reading
	now, and exits. But you presumably already know this.
	
	`python -m Shady help EXAMPLE_NAME`  is equivalent to
	`python -m Shady run EXAMPLE_NAME --help`. Either of these will
	print the documentation for the named example script, and exit.

	You can also request help on a class, function or topic::
	
		python -m Shady help World
		python -m Shady help BackEnd
		python -m Shady help PropertySharing
	
	The last one is the name of a "topic"---these are all symbols
	inside the `Shady.Documentation` sub-module, and one of them is,
	itself, a list of topics: `python -m Shady help Topics`


`version` and `versions`

	`python -m Shady version` displays the version number of the
	Shady Python package.  The `versions` subcommand displays more
	in-depth information.
"""

import os
import sys
import glob
import Shady

from Shady.Console import UnindentCommon, MultilineStrip, TabsToSpaces
def Pretty( x ):
	if hasattr( x, 'split' ): x = x.split( '\n' )
	return TabsToSpaces( UnindentCommon( MultilineStrip( x ) ) )


if not hasattr( sys, 'argv' ): sys.argv = []

def PrintDoc( obj, exit=True ):
	
	print( '\n' + Pretty( obj.__doc__ ) )
	try: constructorDocstring = '\n' + obj.__init__.__doc__
	except: pass
	else:
		if constructorDocstring.strip():
			print( '\n\nInit docstring:\n\n%s\n' % Pretty( constructorDocstring.strip( '\n' ) ) )
	if exit: sys.exit( 0 )

def Help():
	if len( sys.argv ) == 2 and sys.argv[ 1 ] and not sys.argv[ 1 ].startswith( '-' ):
		arg = sys.argv[ 1 ]
		obj = Shady
		pieces = arg.split( '.' )
		if pieces and pieces[ 0 ] == 'Shady': pieces.pop( 0 )
		for piece in pieces:
			obj = getattr( obj, piece, None )
			if obj is None: break
		if obj and getattr( obj, '__doc__', None ):
			PrintDoc( obj, exit=True )
		elif hasattr( Shady.Documentation, arg ):
			PrintDoc( getattr( Shady.Documentation, arg ), exit=True )
		
	if len( sys.argv ) > 1 and sys.argv[ 1 ] and not sys.argv[ 1 ].startswith( '-' ):
		args = [ '--console=None' ] + sys.argv[ 1: ] + [ '--help' ]
		return Shady.Utilities.RunShadyScript( *args )
	else:
		print( __doc__ )
		sys.exit( 0 )

def ListDemos():
	d = Shady.PackagePath( 'examples' )
	print( '\nExample scripts in %s :\n' % d )
	for each in sorted( glob.glob( os.path.join( d, '*.py' ) ) ):
		stem = os.path.splitext( os.path.basename( each ) )[ 0 ]
		summary = [ line[ 2: ].strip() for line in open( each ).read().replace( '\r\n', '\n' ).replace( '\r', '\n' ).split( '\n' ) if line.startswith( '#: ' ) ]
		summary = summary[ 0 ] if summary else ''
		print( '  % 20s   %s' % ( stem, summary ) )
	print( """
To run a script in demo mode:  python -m Shady  demo  SCRIPT_NAME
For more info on a script:     python -m Shady  help  SCRIPT_NAME
""" )

def ListScreens():
	__doc__ = """
	This subcommand lists details for each of the available display
	devices, including the index number that you would pass to a
	`World` constructor if you wanted to use that screen.
	"""
	cmdline = Shady.CommandLine( doc=Pretty( __doc__ ) )
	backend = cmdline.Option( 'backend', default=None, type=( None, str ), position=0, strings=[ 'pygame', 'pyglet', 'ShaDyLib', 'accel', 'glfw' ], doc="""
If specified, this dictates which back-end windowing toolbox 
will be used to query information about screens. The
`BackEnd()` global function will be called with this argument
before calling `Screens()`.

NB: ``ShaDyLib``, `'accel'` and `'glfw'` are synonyms for the
    same thing (the ShaDyLib accelerator uses the GLFW
    windowing toolbox under the hood).
    
""" )
	cmdline.Help().Finalize()
	if backend: Shady.BackEnd( backend )
	print( '' )
	Shady.Screens( pretty_print=True )
	if sys.platform.lower() == 'darwin':
		print( """
NB: screen sizes and offsets are in "screen coordinates". For
    Retina screens on macOS, and depending on the back-end
    you're using, these values may be smaller (by some integer
    factor, such as 2) than the number of actual pixels you will
    have available after you create the `World`. If need to
    specify size/offset explicitly (which usually you would not)
    then use the "screen coordinates". But check the `.size`
    attribute after `World` construction to discover how many
    actual pixels you have.
""" )

subcommands = dict(
	list = ListDemos,
	demo = lambda: Shady.Utilities.RunShadyScript( *sys.argv[ 1: ] ) if sys.argv[ 1: ] else ListDemos(),
	run = lambda: Shady.Utilities.RunShadyScript( '--console=None', *sys.argv[ 1: ] ),
	shell = lambda: Shady.Utilities.RunShadyScript( '--skipShadyInteractionUntilTheEnd', *sys.argv[ 1: ] ),
	# the shell subcommand, or equivalently the '-skipShadyInteractionUntilTheEnd' option, is an undocumented feature for running the script without pauses but then opening an interactive prompt at the end
	test = Shady.Testing.Test,
	timings = lambda: Shady.PlotTimings( sys.argv ),
	version = lambda: sys.stdout.write( Shady.__version__ ),
	versions = lambda: Shady.ReportVersions( importAll=True ),
	screens = ListScreens,
	help = Help,
)

main = 'absent'
if len( sys.argv ) >= 2:
	subcommand = sys.argv[ 1 ].lower()
	if subcommand.lstrip( '-' ) in subcommands: subcommand = subcommand.lstrip( '-' )
	main = subcommands.get( subcommand, 'unrecognized' )
	
if main in [ 'unrecognized', 'absent' ]: main = subcommands[ 'run' ]
else: sys.argv.pop( 1 )
main()
