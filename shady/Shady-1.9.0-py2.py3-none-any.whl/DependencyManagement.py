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
__all__ = [
	'Require', 'RequireShadyVersion',
	'Import',
	'Unimport',
	'RegisterVersion',
	'GetVersions',
	'ReportVersions',
	
	'LoadPyplot',
]

import os
import sys
import platform
import collections

# Force warnings.warn() to omit the source code line in the message
import warnings
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None, **k: formatwarning_orig( message, category, filename, lineno, line='' )

KNOWN = {}
IMPORTED = {}
VERSIONS = collections.OrderedDict()
_SPHINXDOC = any( os.environ.get( varName, '' ).lower() not in [ '', '0', 'false' ] for varName in [ 'SPHINX' ] )

class ModuleNotAvailable( object ):
	def __init__( self, name, packageName=None, broken=False ): self.__name, self.__packageName, self.__broken = name, packageName, broken
	def __bool__( self ): return False    # works in Python 3 but not 2
	def __nonzero__( self ): return False # works in Python 2 but not 3
	def __getattr__( self, attr ): raise ImportError( str( self ) )
	def __str__( self ):
		packageName = self.__packageName
		if packageName and not isinstance( packageName, ( tuple, list ) ): packageName = [ packageName ]
		packageName = ' or '.join( repr( name ) for name in packageName ) if packageName else repr( self.__name )
		if self.__broken:
			msg = 'module %r did not work as expected for this functionality - your installation of the %r package may be broken' % ( self.__name, packageName )
			if self.__broken != 1: msg += ' (%s)' % self.__broken
		else:
			msg = 'module %r could not be imported - you need to install the third-party %s package for this functionality' % ( self.__name, packageName )
		return msg
		
PRETEND_NOT_INSTALLED = []
def Sabotage( *pargs ):
	"""
	This is intended purely for debugging purposes in the hands of Shady's
	maintainers, to get an idea of how Shady behaves in the absence of one
	or more third-party dependencies without having to go to all the
	trouble of setting up a new virtual environment. Pass the names of one
	or more packages/modules and Shady will pretend that they are not
	installed. For maximum effectiveness, hack your `Sabotage()` call into
	the very first line of `Shady/__init__.py`
	"""
	global PRETEND_NOT_INSTALLED
	PRETEND_NOT_INSTALLED += pargs

def RequireShadyVersion( minimumVersion ):
	"""
	Verify that the current version of Shady is equal to, or later than,
	the specified `minimumVersion`, which should be a string encoding three
	integers in 'X.Y.Z' format.
	"""
	currentVersion = GetVersions()[ 'Shady' ] [ 0 ]
	if [ int( x ) for x in currentVersion.split( '.' ) ] < [ int( x ) for x in minimumVersion.split( '.' ) ]:
		raise RuntimeError( 'Shady version %s or later is required (current version is %s)' % ( minimumVersion, currentVersion ) )
	
def Require( *pargs ):
	"""
	Verify that the named third-party module(s) is/are available---if not,
	raise  an exception whose message contains an understandable action
	item for the user.
	""" # TODO: need to handle alternativeNames, packageName somehow
	modules = [ Import( name ) for arg in pargs for name in arg.split() ]
	errors = []
	for module in modules:
		if not module: errors.append( str( module ) )
	if errors and not _SPHINXDOC:
		raise ImportError( '\n   '.join( [ '\n\nOne or more third-party requirements were not satisfied:' ] + errors ) )
	return modules[ 0 ] if len( modules ) == 1 else modules

def Define( canonicalName, alternativeNames=None, packageName=None, registerVersion=False ):
	rec = KNOWN.setdefault( canonicalName, {} )

	if alternativeNames is None: alternativeNames = []
	if isinstance( alternativeNames, str ): alternativeNames = alternativeNames.split()
	seq = rec.setdefault( 'alternativeNames', [] )
	for name in alternativeNames:
		if name not in seq: seq.append( name )

	if packageName is None: packageName = []
	if isinstance( packageName, str ): packageName = packageName.split()
	seq = rec.setdefault( 'packageName', [] )
	for name in packageName:
		if name not in seq: seq.append( name )

	rec.setdefault( 'registerVersion', False )
	if registerVersion: rec[ 'registerVersion' ] = registerVersion

	return rec[ 'alternativeNames' ], rec[ 'packageName' ], rec[ 'registerVersion' ]

def ImportAll():
	return [ Import( name ) for name in KNOWN ]
	
def Import( canonicalName, *alternativeNames, **kwargs ):
	alternativeNames, packageName, registerVersion = Define( canonicalName=canonicalName, alternativeNames=alternativeNames, **kwargs )
	names = [ canonicalName ] + list( alternativeNames )
	pretendNotInstalled = any( name in PRETEND_NOT_INSTALLED for name in names )
	for name in names:
		if pretendNotInstalled: name += '_NOT'
		module = IMPORTED.get( name, None )
		if module is not None: return module
		try: exec( 'import ' + name )
		except ImportError: module = ModuleNotAvailable( canonicalName, packageName )
		except: module = ModuleNotAvailable( canonicalName, packageName, broken=True )
		else:
			module = sys.modules[ name ]
			IMPORTED[ module.__name__ ] = module
			break
	if registerVersion: RegisterVersion( module )
	return module

def Unimport( *names ):
	names = [ getattr( name, '__name__', name ) for name in names ]
	prefixes = tuple( [ name + '.' for name in names ] )
	for registry in [ sys.modules, IMPORTED, VERSIONS ]:
		names = [ name for name in registry if name in names or name.startswith( prefixes ) ]
		for name in names: registry.pop( name )

def RegisterVersion( module=None, attribute='__version__', name=None, value=None ):
	if module and not name:
		name = module.__name__
		if attribute.strip( '_' ).lower() != 'version': name += '.' + attribute
	if module and not value:
		value = getattr( module, attribute, None )
	if name and value:
		VERSIONS[ name ] = value
	return module
	
def GetVersions():
	versions = VERSIONS.__class__()
	for k, v in VERSIONS.items():
		if callable( v ): versions.update( v() )
		elif v: versions[ k ] = v
	return versions

def ReportVersions():
	for k, v in GetVersions().items():
		print( '%25s : %r' % ( k, v ) )

def LoadPyplot( interactive=None ):
	matplotlib = plt = Import( 'matplotlib', registerVersion=True )
	if matplotlib: import matplotlib.pyplot as plt
	if matplotlib and interactive is not None: matplotlib.interactive( interactive )
	return plt

RegisterVersion( name='sys', value=sys.version )
RegisterVersion( name='sys.platform', value=sys.platform )
RegisterVersion( name='platform.machine', value=platform.machine() )
RegisterVersion( name='platform.architecture', value=platform.architecture() )
for func in 'win32_ver mac_ver linux_distribution libc_ver'.split():
	try: result = getattr( platform, func )()
	except: result = ( '', )
	if result and result[ 0 ]:
		RegisterVersion( name='platform.' + func, value=result )
