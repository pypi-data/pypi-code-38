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
Aside from a couple of internal routines for automatic doc generation,
this module is designed to contain enpty classes whose names and
docstrings explain some of the broader concepts of Shady.

Examples of use - from IPython, using `?` syntax::

	In [1]: import Shady
	
	In [2]: Shady.Documentation.ManagedProperties?
	                            ^ tab-completion is your friend here

Or from a vanilla Python prompt:

	>>> import Shady
	>>> help( Shady.Documentation.ManagedProperties )

"""

__all__ = [
	# will be filled automatically...
]

import os       as _os
import re       as _re
import glob     as _glob
import inspect  as _inspect
import textwrap as _textwrap
from .Rendering import Screens, World, Stimulus, __meta__

_INTERPS = dict( __meta__ )
_INTERPS[ 'listOfWorldProperties'    ] = '\n'.join( p.rst( 'Shady.World'    ) for p in World.Properties()    if p.doc )
_INTERPS[ 'listOfStimulusProperties' ] = '\n'.join( p.rst( 'Shady.Stimulus' ) for p in Stimulus.Properties() if p.doc )
class Indenter( object ):
	def __init__( self, *pargs, **kwargs ):
		self.things = dict( *pargs, **kwargs )
	def __getitem__( self, arg ):
		key = arg.lstrip()
		prefix = arg[ :-len( key )  ]
		txt = str( self.things[ key ] )
		return ''.join( prefix + line for line in _textwrap.dedent( txt.replace( '\t', '    ' ) ).splitlines( True ) ).strip()
_INTERPS[ 'indent' ] = Indenter( _INTERPS )

try: __file__
except NameError:
	try: frame = _inspect.currentframe(); __file__ = _inspect.getfile( frame )
	finally: del frame  # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
_HERE = _os.path.dirname( _os.path.realpath( __file__ ) )
_DOCDIR = _os.path.realpath( _os.path.join( _HERE, '..', '..', 'doc' ) )
_AUTODIR = _os.path.join( _DOCDIR, 'auto' )
_SPHINXDOC = any( _os.environ.get( varName, '' ).lower() not in [ '', '0', 'false' ] for varName in [ 'SPHINX' ] )
_MATCH_RST = [
	[ 'crossref',    _re.compile(    r':doc:`(.*?)\s*(<[a-z0-9_\-\+\.]+>)?`(_+)?', _re.I ),  lambda m: _os.path.basename( m.groups()[ 0 ] ) ],
	[ 'pyobj',       _re.compile( r':py:obj:`(.*?)\s*(<[a-z0-9_\-\+\.]+>)?`', _re.I ),  r'`\1`' ],
	[ 'option',      _re.compile(               r'^\s+:[a-z0-9_\-]+:\s+.*?\n', _re.I | _re.M ),  '' ],
	[ 'objlink',     _re.compile( r'\|(\S+?)\|_?' ),  r'`\1`' ],
	[ 'backticks',   _re.compile( r'``' ), '`' ],
	[ 'role',        _re.compile( r':[a-z0-9_]+:`(.*?)\s*(<[a-z0-9_\-\+\.]+>)?`(_+)?', _re.I ),  r'\1' ],
	#[ 'comment',     _re.compile( r'\n[\t ]*\.\.[\t ]*[a-z0-9_]+(:+.*)?(\n[\t ]*(?=\n))?', _re.I ), '' ],
	[ 'directive',   _re.compile( r'(?<=\n)[\t ]*\.\.[^\n]+\n*(?=\n)?' ), '' ],
	[ 'examples_*',  _re.compile( r'^(\s+)examples_([a-zA-Z0-9_\-\+]+)\s*$', _re.MULTILINE ), r'\1examples/\2.py' ],
	[ 'doublecolon', _re.compile( r'(?<=\n)[\t ]*::([\t ]*\n)+' ), '' ],
	[ 'doublecolon', _re.compile( r':(?=:[\t ]*\n)' ), '' ],
	[ 'hyperlink',   _re.compile(             r'`(.*?)\s*(<[^<>]+?>)?`_+',    _re.I ),  lambda m: m.groups()[ 0 ] ],
]
_MATCH_TITLE = _re.compile( r'\s*([\S ]+)[\t ]*\n[\-\^\=\~]{3,}[\t ]*\n' )
_RST = {}

	
class _DynamicDocString( object ):
	def __set__( self, instance, value ): instance.__class__._doc = value
	def __get__( self, instance, owner=None ):
		doc = owner._doc
		if not _SPHINXDOC:
			for name, match, replace in _MATCH_RST:
				doc = _re.sub( match, replace, doc )
		return doc.lstrip( '\n' ).rstrip()
_DocumentationOnly = type
if 1:
	class _DocumentationOnly( type ):
		def __str__( self ): return '(this class only exists for its docstring)'
		def __repr__( self ): ''; return self.__doc__
	_DocumentationOnly.__name__ = 'DocumentationOnly'

def _extract( rst, keyword ):
	m = _re.search( r'\n[\t ]*\.\.[\t ]*' + keyword + '(:+\s*(.+?))\s*\n', rst, _re.I | _re.MULTILINE )
	if m: return m.group( 2 )

def _as_filename( x, locations=( '.', 'rst' ) ):
	if '\n' in x: return
	if _os.path.isfile( x ): return _os.path.realpath( x )
	if _os.path.isabs( x ): return
	for location in locations:
		attempt = _os.path.join( _HERE, location, x )
		if _os.path.isfile( attempt ): return _os.path.realpath( attempt )		
	
def _doc( doc, name=None ):
	source_filename = _as_filename( doc )
	if source_filename: doc = open( source_filename, 'rt' ).read().replace( '\r\n', '\n' ).replace( '\r', '\n' )
	doc = '\n' + doc.lstrip( '\n' ).rstrip() + '\n'
	doc = doc.replace( '\t', ' ' * 4 )
	try: doc = doc.format( **_INTERPS )
	except Exception as err: pass # print( 'Doc interpolation error in %r: %r' % ( source_filename, err ) )
	names = filename = None
	if name: names = name.strip().replace( '-', ' ' ).title().replace( ' ', '' )
	#names = _extract( doc, 'objectname' )
	#filename = _extract( doc, 'filename' )
	if source_filename:
		stem = _os.path.splitext( _os.path.basename( source_filename ) )[ 0 ]
		if not names: names = stem
		if not filename: filename = stem
	if not names:
		match = _re.match( _MATCH_TITLE, doc )
		if match: names = match.groups()[ 0 ].strip().replace( '-', ' ' ).title().replace( ' ', '' )
		elif source_filename: names = _os.path.splitext( _os.path.basename( source_filename ) )[ 0 ]
		else: names = None
	if not names: raise ValueError( 'failed to infer name of doc object %r' % ( source_filename if source_filename else doc[ :50 ] ) )
	if isinstance( names, str ): names = names.replace( ',', ' ' ).split()
	names = [ name.lstrip( '0123456789_-' ) for name in names ]
	doc = '\n.. top:\n' + doc
	# Use _DocumentationOnly as a metaclass for a new class, in a Python2- and Python3-compatible way:
	wrapper = _DocumentationOnly( names[ 0 ] if names else 'DocumentationOnly', (), dict(
		__slots__ = [],
		__doc__ = _DynamicDocString(),
		_doc = doc,
		_names = names,
		_filename = filename,
		_source_filename = source_filename,
	) )
	def wrapper_init( self ): ''; pass
	wrapper.__init__ = wrapper_init  # neutralize boilerplate __init__ docstring
	def resemble_own_docstring( self ): ''; return self.__doc__
	wrapper.__repr__ = resemble_own_docstring # this is what instances of the class (which never need to be created) look like on the console
	for name in names:
		globals()[ name ] = wrapper
		break # comment this out to assign all names to this module's namespace; retain it to assign only the canonical names...
	if names: __all__.append( names[ 0 ] ) # ...but either way, export canonical names only
	return wrapper

def _auto_compose_rst():
	# first, the example scripts (updating the ExampleScripts index doc as we go)
	packageLocation = _HERE.replace( '\\', '/' ).rstrip( '/' ) + '/'
	examples = sorted( _glob.glob( packageLocation + 'examples/*.py' ) )
	for i, fullFilePath in enumerate( examples ):
		shortFilePath = fullFilePath.replace( '\\', '/' )[ len( packageLocation ): ]
		literalIncludePath = _os.path.relpath( fullFilePath, _AUTODIR )
		stem, xtn = _os.path.splitext( _os.path.basename( shortFilePath ) )
		rstStem = 'examples_' + stem
		tocEntry = '   %s\n' % rstStem
		#oneLineSummary = [ line[ 2: ].strip() for line in open( fullFilePath ,'rt' ).read().replace( '\r\n', '\n' ).replace( '\r', '\n' ).split( '\n' ) if line.startswith( '#:' ) ]
		#oneLineSummary = ' :  ' +  oneLineSummary[ 0 ] if oneLineSummary else ''
		#tocEntry = '   %s%s <%s>\n' % ( shortFilePath, oneLineSummary, rstStem )  # for including the one-line summary in the hyperlink text of each toc entry
		#tocEntry = '* :doc:`%s <%s>` %s\n' % ( shortFilePath, rstStem, oneLineSummary )  # for including links and one-line summaries in a vanilla bulleted list (not a toc - remove .. toctree directive from NNN_Examples.rst )
		if stem == 'showcase':
			ExampleScripts._doc = ExampleScripts._doc.format( **locals() ) # fills in {stem} and {shortFilePath} for first example
		ExampleScripts._doc += tocEntry
		title = shortFilePath
		underline = '=' * len( title )
		_RST[ rstStem ] = """\
{title}
{underline}

This is one of the :doc:`example scripts <ExampleScripts>` included
with Shady. These scripts can be run conventionally like any
normal Python script, or you can choose to run them as
interactive tutorials, for example with `python -m Shady demo {stem}`

.. literalinclude:: {literalIncludePath}

""".format( **locals() )

	# And now everything else:
	for name in __all__:
		obj = globals()[ name ]
		try: ( obj._filename, obj._names, obj._doc )
		except: continue
		filename = obj._filename
		if not filename and obj._names: filename = obj._names[ 0 ]
		if filename: filename = filename.lstrip( '0123456789_-' )
		if not filename: continue
		_RST[ filename ] = obj._doc

def _generate_rst_files( dummy=False ):
	if not _os.path.isdir( _DOCDIR ): print( 'Directory not found: ' + _DOCDIR ); return
	if not _os.path.isdir( _AUTODIR ): _os.makedirs( _AUTODIR )
	oldFiles = sorted( _glob.glob( _os.path.join( _AUTODIR, '*.rst' ) ) )
	for oldFile in oldFiles:
		print( 'removing ' + oldFile )
		if not dummy: _os.remove( oldFile )
	for fileStem, content in sorted( _RST.items() ):
		fileName = fileStem + '.rst'
		filePath = _os.path.join( _AUTODIR, fileName )
		print( 'writing ' + filePath )
		if dummy: continue
		with open( filePath, 'wt' ) as fh: fh.write( content + '\n' )

################################################################################
################################################################################

for _filename in sorted( _glob.glob( _os.path.join( _HERE, 'rst', '*.rst' ) ) ): _doc( _filename )

_ALREADY_COVERED = []
def _toctree( name, entries, text='', title=None, **flags ):
	if isinstance( entries, str ): entries = entries.split()
	_ALREADY_COVERED.extend( entry.split( '/' )[ -1 ] for entry in entries )
	_ALREADY_COVERED.append( name )
	if text: text = '\n' + text.strip() + '\n'
	if title is None: title = name
	layout = """
{title}
{underscore}
{text}
.. toctree::
   {flags}
   
   {entries}
"""
	flags.setdefault( 'maxdepth', 2 )
	flags = '\n   '.join( ':%s: %s' % item for item in flags.items() ) 
	content = layout.format( title=title, underscore='=' * len( title ), text=text, flags=flags, entries='\n   '.join( entries ) )
	return _doc( content, name=name )

if _SPHINXDOC:
	_ALREADY_COVERED.append( 'Welcome' )
	_toctree( name='Contents', title='', caption='Table of Contents', entries="""
		auto/Overview
		auto/Setup
		auto/GettingStarted
		auto/KeyConcepts
		source/modules
		auto/License
		""",
	) # using directoryName/fileName purely because this will be `..include::`d in a top-level doc.  Others will not.
	_toctree( name='Setup', entries='Installation Compatibility Accelerator' )
	_toctree( name='Getting Started', entries='Concurrency CommandLineOptions ExampleScripts', text="""
The best way to learn about Shady is to use our :doc:`ExampleScripts` as interactive
tutorials.  The best one to start with is `python -m Shady demo showcase`. Others
can be listed with `python -m Shady list`.  The topics below go into more detail
about the different ways of starting Shady:
""" )
	_toctree( name='Key Concepts', entries=[ name for name in __all__ if name not in _ALREADY_COVERED ] )

else:
	_toctree( 'Topics', [ name for name in __all__ ] )

################################################################################
################################################################################
_auto_compose_rst()
