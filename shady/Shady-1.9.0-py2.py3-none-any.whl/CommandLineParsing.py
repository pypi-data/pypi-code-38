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
A general-purpose command-line parser (class CommandLine). 

Note that everything exported from this module is also available in
the top-level `Shady.*` namespace.

If I had known about `argparse` at the time, I probably wouldn't
have written this submodule, but it is simpler to use while having
many nice additional features.

Note that it allows only a constrained subset of the mess of command-
line conventions, designed to allow easy mapping onto Python variables
and function calls. Here is an outline of some of the main interface
features:

* ALL arguments have names, and can be addressed by name in arbitrary
  order. So, there is no such thing as a purely "positional" argument.
  However, a numeric `position` *may* be assigned to an option when
  it is defined in the program: if so, the value will be filled in
  from unnamed command-line arguments, if any, as required. This is
  directly analogous to the way arguments are specified when you call
  a function in Python.

* There are no "short versions" of argument names (e.g. `-v` as
  synonym for `--verbose`). To remove ambiguity and confusion, and
  again to maintain the analogy with Python function calls, each
  argument has exactly one name.  By default, double-dashes are
  required before an option name, although the parser can be
  configured to allow single-dash or even dashless naming.

* Options do not "gobble up" subsequent arguments. Equals-signs are
  required if you want to supply an option value. So the scope of
  one option is always exactly one command-line argument (and hence
  one space-delimited string on the command line, unless quotes are
  used). For example, to specify the value of an option called
  `logfile`, you cannot say `--logfile foo.txt`. Instead you have to
  say `--logfile=foo.txt`.

* If `bool` is one of the allowable types in an option definition,
  then the `=True` or `=1` substring can be omitted on the command
  line when specifying a true value for that option. So for example,
  `--verbose` would be equivalent to `--verbose=True`. (To specify
  a false value explicitly, you would have to say `--verbose=False`
  or `--verbose=0` in full.)

* There is no way to specify a variadic option. But you can
  `.Delegate()` processing of anything your first `CommandLine`
  instance has not recognized, to subsequent differently-configured
  instances.

"""
__all__ = [
	'CommandLine',
]
import re
import sys
import ast
import copy
import shlex
import textwrap

KVDELIMS = ( '=', ':' )


Unspecified = object()
Taken = object()
try: BaseException
except NameError: BaseException = Exception # in Python 2, errors inherit from StandardError, non-errors from Exception
try: StandardError
except NameError: StandardError = Exception  # in Python 3, errors inherit from Exception, non-errors from BaseException
# now in either, you can inherit errors from StandardError and non-errors from BaseException. Would that have been so hard, Guido?

class CommandLineHelp( BaseException ): pass
class CommandLineError( StandardError ): pass
class CommandLineValueError( CommandLineError ):
	def __init__( self, arg, explanation ):
		CommandLineError.__init__( self, 'illegal value in command-line option %s (%s)' % ( arg, explanation ) )
		
def AlternativesString( sequence, transformation=repr ):
	sequence = [ transformation( x ) for x in sequence ]
	return ', '.join( sequence[ :-1 ] ) + ( len( sequence ) > 1 and ' or ' or '' ) + sequence[ -1 ]

def Indent( s, indent='    ' ):
	if s.endswith( '\n' ): s, ending = s[ :-1 ], '\n'
	else: ending = ''
	return ( ( '\n' + s ).replace( '\n', '\n' + indent ) + ending )[ 1: ]

def Wrap( s, width=78 ):
	return '\n'.join( textwrap.wrap( s, width ) )
	
class OptionSchema( object ):
	def __init__( self, default_position, dashes, **kwargs ):
		self.__dict__.update( { k : Unspecified for k in 'name default position type min max values strings length minlength maxlength allowpartial casesensitive doc section'.split() } )
		spec = sorted( kwargs.items() )
		for k, v in spec:
			invk = k.lower().replace( '_', '' )
			if invk not in self.__dict__:
				if k.startswith( '_' ): raise ValueError( 'unrecognized attribute %r' % k )
				#elif self.name is Unspecified: self.name, self.default = k, v; continue
				else: raise ValueError( 'unrecognized attribute %r (cannot interpret it as the option name, because %r has already been used for this)' % ( k, self.name ) )
			previousValue = self.__dict__[ invk ]
			if previousValue is Unspecified: self.__dict__[ invk ] = v
			#elif self.name is Unspecified and not k.startswith( '_' ): self.name, self.default = k, v; continue
			else: raise ValueError( 'duplicate attribute %r: %s=%r has already been set' % ( k, invk, previousValue ) )
		if self.name is Unspecified: raise ValueError( 'no name was specified for this option' )
		if self.default is Unspecified and self.position is Unspecified:  self.position = default_position
		self.dashes = dashes
		if self.type is Unspecified: self.type = ()
		elif not isinstance( self.type, ( tuple, list ) ): self.type = [ self.type ]
		if self.strings is Unspecified: self.strings = ()
		elif not isinstance( self.strings, ( tuple, list ) ): self.strings = self.strings.split()
		if self.values is Unspecified: self.values = ()
		elif not isinstance( self.values, ( tuple, list ) ): self.values = [ self.values ]
		if self.length is Unspecified: self.length = ()
		elif not isinstance( self.length, ( tuple, list ) ): self.length = [ self.length ]
		if self.allowpartial  is Unspecified: self.allowpartial  = True
		if self.casesensitive is Unspecified: self.casesensitive = False
		if self.doc is Unspecified: self.doc = ''
	def Report( self ):
		d = dict( self.__dict__ )
		name = d.pop( 'name' )
		s = '-' * max( d.pop( 'dashes' ) ) + name
		default = d.pop( 'default' )
		if default is not Unspecified:
			defaultStr = '=' + repr( default )
			if not isinstance( default, str ): defaultStr = defaultStr.replace( ' ', '' )
			s += defaultStr
		type = d.pop( 'type' )
		if type is not Unspecified:
			try: type = tuple( type )
			except: type = ( type, )
			s += ' (%s)' % ', '.join( getattr( t, '__name__', str( t ) ) for t in type )
		doc = d.pop( 'doc' )
		d.pop( 'section' )
		d.pop( 'position' )
		if not d.get( 'length', () ): d.pop( 'length' )
		if not d.get( 'values', () ): d.pop( 'values' )
		if not d.get( 'strings', () ) or str not in type: d.pop( 'strings' )
		if not d.get( 'strings', () ): d.pop( 'casesensitive' ); d.pop( 'allowpartial' )
		for k, v in d.items():
			if v is not Unspecified: s += '\n    %s = %r' % ( k, v )
		if doc: s += '\n' + Indent( doc if '\n' in doc else Wrap( doc ) )
		return s
	def Resolve( self, args_p, args_k, optsOut=None ):
		whole = [ '-' * n + self.name for n in self.dashes ]
		prefixes = tuple( [ x + delim for x in whole for delim in KVDELIMS ] )
		sources = []
		value = Unspecified
		for originalPosition, arg in args_k[ ::-1 ]:
			if arg in whole or arg.startswith( prefixes ):
				matchedType = 'k'
				sources.append( ( originalPosition, matchedType ) )
				if value is Unspecified:
					matchedArg = arg
					value = arg.lstrip( '-' )[ len( self.name ): ]
					if len( value ) == 0: value = True  # so --verbose ends up the same as --verbose=1
					elif value.startswith( KVDELIMS ): value = value[ 1: ]
		if value is Unspecified:
			if self.position is not Unspecified and 0 <= self.position < len( args_p ):
				originalPosition, value = args_p[ self.position ]
				matchedArg = repr( value ) + ( ' when interpreted as --%s option' % self.name )
				matchedType = 'p'
				sources.append( ( originalPosition, matchedType ) )
			elif self.default is not Unspecified:
				value = self.default
				matchedArg = 'default value'
				matchedType = 'd'
			else: raise CommandLineError( 'option --%s was not specified on the command line, and has no default value' % self.name )
		if isinstance( value, str ):
			try: literal = ast.literal_eval( value )
			except: literal = Unspecified
		else: literal = value
		if self.type:
			for t in self.type:
				if t in [ None ] and literal is None: value = None; break
				if t in [ bool ] and literal in [ True, False ]: value = bool( literal ); break 
				if t in [ str ]:
					if isinstance( literal, str ): value = literal
					for permittedSet in [ list( self.values ) + list( self.strings ), self.strings ]:
						if permittedSet:
							transform = str if self.casesensitive else ( lambda x: str( x ).lower() )
							def match( allowed, incoming ):
								allowed, incoming = transform( allowed ), transform( incoming )
								if incoming == allowed: return True
								return self.allowpartial and incoming and allowed.startswith( incoming )
							matched = [ s for s in permittedSet if match( s, value ) ]
							if len( matched ) == 1: value = matched[ 0 ]
							elif len( matched ) > 1: raise CommandLineValueError( matchedArg, 'ambiguous - could match ' + AlternativesString( matched ) )
							else: raise CommandLineValueError( matchedArg, 'value must be ' + AlternativesString( permittedSet ) )
					break
				if t in [ int, float, bool ]:
					try: numeric = float( value )
					except: continue
					if t is not float and numeric != t( numeric ): continue
					value = t( numeric )
					if self.min is not Unspecified and value < self.min: raise CommandLineValueError( matchedArg, 'minimum is %r' % self.min )
					if self.max is not Unspecified and value > self.max: raise CommandLineValueError( matchedArg, 'maximum is %r' % self.max )
					break
				if isinstance( t, type ) and isinstance( literal, t ) and literal is not Unspecified: value = literal; break
			else:
				raise CommandLineValueError( matchedArg, 'could not interpret as ' + AlternativesString( self.type, lambda t: getattr( t, '__name__', t.__class__.__name__ ) ) )
		if not isinstance( value, str ) and self.values and value not in self.values: raise CommandLineValueError( matchedArg, 'value must be ' + AlternativesString( self.values ) )
		try: length = len( value )
		except: pass
		else:
			if self.length and length not in self.length: raise CommandLineValueError( matchedArg, 'length must be ' + AlternativesString( self.length ) )
			if self.minlength is not Unspecified and length < self.minlength: raise CommandLineValueError( matchedArg, 'length cannot be less than %r'    % self.minlength )
			if self.maxlength is not Unspecified and length > self.maxlength: raise CommandLineValueError( matchedArg, 'length cannot be greater than %r' % self.maxlength )
		if optsOut is not None: optsOut[ self.name ] = value
		return sources, value

	
class Bunch( dict ):
	def __init__( self, *pargs, **kwargs ): self.__dict__ = self.update( *pargs, **kwargs )
	def update( self, *pargs, **kwargs ): [ dict.update( self, d ) for d in pargs + ( kwargs, ) ]; return self
	def release( self ): self.__dict__ = {} # call this to remove the circular self-reference and allow the object to be deleted


class CommandLine( object ):
	"""
	`c = CommandLine()`
		Create the object. Uses `argv=sys.argv[1:]` by default, as well as
		`doc=__doc__`. 
	
	`c.Option(...)`
		Define an option.  By default, the option name and resolved value will be stored
		as key and value in the dict `c.opts`. If you specify another `container` it will
		be stored there instead (and if you say `container=None`, it will not be stored
		anywhere).  In any case the resolved value will also be returned from `.Option()`
		
	`c.Help()`
		Define and process the `--help` option: if it was supplied, print documentation
		and then either `sys.exit()` or `raise CommandLineHelp()`.
		
	`c.Finalize()`
		Issue an error if there are unrecognized options.
		
	`c.Delegate()`
		An alternative to `.Finalize()`. Returns `argv` with all already-recognized
		options removed, so you can pass it to the next `CommandLine` parser in the
		cascade (in cases where you have more than one).
	"""
	def __init__( self, argv=None, dashes=2, doc='' ):
		self.__args = { 'p' : [], 'k' : [] }
		self.__dashes = tuple( dashes ) if isinstance( dashes, ( tuple, list ) ) else ( dashes, )
		self.__schema = []
		self.__used = []
		self.__sectionNames = [ '' ]
		self.doc = doc
		self.opts = Bunch()
		if isinstance( argv, str ): argv = shlex.split( argv )
		elif argv is None:
			if not hasattr( sys, 'argv' ): sys.argv = []
			if not sys.argv: sys.argv.append( sys.executable )
			argv = sys.argv[ 1: ]
		self.__argv = argv
		for originalPosition, arg in enumerate( argv ): self.__args[ self._ArgType( arg ) ].append( ( originalPosition, arg ) )
	dashes = property( lambda self: self.__dashes )
	def _ArgType( self, arg ):
		if not isinstance( arg, str ): return 'p'
		allowableDashes = self.__dashes
		stripped = arg.lstrip( '-' )
		nDashes = len( arg ) - len( stripped )
		leadingAlpha = len( stripped ) and stripped[ 0 ].lower() in 'abcdefghijklmnopqrstuvwxyz'
		if 0 in allowableDashes and leadingAlpha and any( delim in arg for delim in KVDELIMS ): return 'k' # note that this excludes anything that starts with a quote
		elif nDashes and nDashes in allowableDashes and leadingAlpha: return 'k'
		else: return 'p'
	def Option( self, name, default=Unspecified, container=Unspecified, **kwargs ):
		schema = self.__schema
		opt = OptionSchema( len( schema ), self.__dashes, name=name, default=default, **kwargs )
		if opt.section is Unspecified: opt.section = self.__sectionNames[ -1 ]
		schema.append( opt )
		if container is Unspecified: container = self.opts
		sources, value = opt.Resolve( self.__args[ 'p' ], self.__args[ 'k' ], container )
		self.__used += sources
		return value
	def Section( self, name=Unspecified ):
		if name is Unspecified: return self.__sectionNames[ -1 ]
		if not name: name = ''
		if self.__sectionNames[ -1 ] in self.__sectionNames[ :-1 ]: self.__sectionNames.pop( -1 )
		self.__sectionNames.append( name )
		return self
	def Help( self, optionName='help', sort=False, after='exit' ):
		help = self.Option( optionName, False, type=bool, container=None, doc='Display this message%s.' % ( ' and exit' if after == 'exit' else '' ) )
		if help: self.DisplayHelp( sort=sort, after=after)
		return self
	def DisplayHelp( self, sort=False, after='exit' ):
		print( '' )
		if self.doc: print( '%s\n' % self.doc )
		positional = list( zip( *sorted( ( opt.position, opt.name ) for opt in self.__schema if opt.position is not Unspecified ) ) )
		if positional: print( 'Positional arguments:\n\n    %s\n\n' % ' '.join( positional[ -1 ] ) )
		if sort:
			opts = sorted( self.__schema, key=lambda x: x.name )
			sections = [ '' ]
			sections_used = [ '' ] if opts else []
		else:
			opts = self.__schema
			sections = self.__sectionNames
			sections_used = { opt.section for opt in opts }
		for section in sections:
			if section not in sections_used: continue
			sectionStr = section if section else 'Keyword arguments (and their defaults)'
			print( sectionStr + ':\n' )
			for opt in opts:
				#if opt.name == optionName and not sort: continue
				if opt.section != section and not sort: continue
				print( Indent( opt.Report() ) + '\n' )
			print( '' )
		if after == 'exit': sys.exit( 0 )
		elif after == 'raise': raise CommandLineHelp()
		return self
	def Finalize( self ):
		usedPositions, usedTypes = zip( *self.__used ) if self.__used else [ [], [] ]
		for originalPosition, arg in self.__args[ 'k' ]:
			if originalPosition not in usedPositions:
				pattern = '|'.join( re.escape( delim ) for delim in KVDELIMS )
				raise CommandLineError( 'could not interpret command-line argument %r (unrecognized option %s)' % ( arg, re.split( pattern, arg, 1 )[ 0 ] ) )
		for originalPosition, arg in self.__args[ 'p' ]:
			if originalPosition not in usedPositions:
				raise CommandLineError( 'unexpected argument %r' % ( arg ) )
		return self
	def Delegate( self, argv=None ):
		if argv is None: argv = self.__argv
		used = dict( p=object(), k=object() )
		for originalPosition, argType in self.__used: argv[ originalPosition ] = used[ argType ]
		while argv and argv[ 0 ] in used.values(): argv.pop( 0 )
		argv[ : ] = [ arg for arg in argv if arg is not used[ 'k' ] ]
		if used[ 'p' ] in argv: raise CommandLineError( 'unexpected argument %r' % argv[ 0 ] )
		return argv
	def Release( self ):
		self.opts.release()

if __name__ == '__main__':
	
	cmdline = CommandLine() # sys.argv[ 1: ] is the default
	mode    = cmdline.Option( 'subcommand', type=str, position=0, strings=[ 'divide', 'exponentiate', 'help' ], allowPartial=True, caseSensitive=False )
	integer = cmdline.Option( 'integer', default=False, type=bool, doc='Whether to convert the numerical result to an integer (rounding down if necessary).' )
	if mode == 'help': cmdline.DisplayHelp()
	sys.argv[ 1: ] = cmdline.Delegate()
	print( cmdline.opts )
	
	subcmdline = CommandLine() # sys.argv[ 1: ] is the default
	if mode == 'divide':
		numerator   = subcmdline.Option( 'numerator',   default=1.0, position=0, type=( float ) )
		denominator = subcmdline.Option( 'denominator', default=2.0, position=1, type=( float ) )
		subcmdline.Help().Finalize()
		result = numerator / denominator
	if mode == 'exponentiate':
		base     = subcmdline.Option( 'base',     default=2.0, position=0, type=( float ) )
		exponent = subcmdline.Option( 'exponent', default=2.0, position=1, type=( float ) )
		subcmdline.Help().Finalize()
		result = base ** exponent
		
	print( subcmdline.opts )
	if integer: result = int( result )
	print( 'result = %r' % result )
