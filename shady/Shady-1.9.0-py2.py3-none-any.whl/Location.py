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
import os
import glob
import inspect

__all__ = [
	'PackagePath',
	'PACKAGE_LOCATION',
	'EXAMPLE_MEDIA',
]

try: __file__
except NameError:
	try: frame = inspect.currentframe(); __file__ = inspect.getfile( frame )
	finally: del frame  # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	
PACKAGE_LOCATION = os.path.dirname( os.path.realpath( __file__ ) )

def PackagePath( *pieces ):
	return os.path.realpath( os.path.join( PACKAGE_LOCATION, *pieces ) )

class ResourceFinder( object ):
	def __init__( self, *root ):
		self.__root = PackagePath( *root )
	def __getattr__( self, attrName ):
		path = os.path.join( self.__root, attrName )
		candidates  = sorted( glob.glob( path + '.*' ) )
		if candidates: return candidates[ 0 ]
		if os.path.exists( path ): return path
		raise IOError( 'could not find resource %s.*' % path )
	def _listdir( self ):
		files = glob.glob( os.path.join( self.__root, '*' ) )
		return { os.path.splitext( os.path.basename( file ) )[ 0 ] : file for file in files if os.path.isfile( file ) }
	def __dir__( self ):
		return sorted( self._listdir().keys() )

EXAMPLE_MEDIA = ResourceFinder( 'examples', 'media' )
