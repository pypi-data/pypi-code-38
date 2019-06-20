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
To activate Shady's ability to render text, you have to explicitly::

    import Shady.Text

This is a break from Shady's usual behavior of arriving with all
batteries included. The reason is that this import can take several
seconds, as Shady (via the third-party package `matplotlib`, if
available) collates a list of available fonts. (For some reason,
even in the twenty-first century, it is a universal truth that the
initialization of any application that wants a few dozen fonts
to be available must be ridiculously time-consuming.)

The third-party packages `numpy` and `pillow` (or `PIL`) are
required.  The `matplotlib` package is optional, but without it you
will be limited to one font (monaco).

Once activated, you probably do not need direct access to anything
inside the `Shady.Text` submodule.  Instead you can just work with
the `.text` property of any `Shady.Stimulus` object.  It can be as
simple as::

    import Shady.Text
    w = Shady.World()
    s = w.Stimulus( text='Hello, World!' )

You can assign a string to the `Stimulus` property `.text`, but
what that really does is create an instance of type `TextGenerator`
which has a number of sub-properties. In fact, assigning a string
to `s.text` is really a syntactic shortcut for creating the
`TextGenerator` instance `s.text` if it doesn't already exist,
then assigning the string to the sub-property `s.text.string`.
Subproperties are accessible in the `Stimulus()` constructor, and
also as (dynamic-assignment-capable) properties of the `Stimulus`
instance itself, using an underscore-delimited notation::

    s = w.Stimulus( text='Hello, World!', text_font='times', text_size=100 )

Note that, in contrast to Shady's usual way of doing things, any
change to the content, style or appearance of a piece of text
requires the CPU to do the rendering work and then transfer the
resulting image texture from CPU to GPU. This will very quickly
cause frame skips if you want to change the content of a large
text image frequently.

The subproperties are as follows:

`.family`, a.k.a. `.family_name`, `.font`, `.font_family`, `.font_name`:
	
	Assign a string here, and Shady will attempt to find a font
	whose name contains all the words in that string. If no match
	can be found, the `.font_found` property will be `False`.

`.bold`, `.italic`, `.black`, `.heavy`, `.light`, `.regular`, etc...:
	
	These style properties will be present to the extent that the
	operating system has fonts installed whose names end with these
	words. Each one is a boolean property that allows you to toggle
	its respective style on or off.  They may or may not work for
	any given font (e.g. the "bold" version of a given font may not
	exist on your system). You can always query the `.font_found`
	property to discover whether it has worked.

`.style`:

	This is an alternative way of controlling font style. You can
	assign a string containing one or more style words here, for
	example `'bold italic'`. As explained above, this may or may
	not succeed depending on what your current font provides.

`.font_found`:

	This read-only property is a boolean value that indicates whether
	the requested font family name and style can be found. If not,
	the stimulus will render text in Shady's built-in default font
	(monaco). This will always be the case if the third-party package
	`matplotlib` is not installed, because `matplotlib` is required
	in order to access the operating system's fonts.

`.emWidthInPixels`,  a.k.a.  `.em`:

	By default, this is `None`, because by default the size of your
	font is specified by `.lineHeightInPixels` (a.k.a `size`).
	If you assign a value here, `.lineHeightInPixels` will become
	`None`, and the font size will be chosen such that the lower-case
	letter "m" is this many pixels wide.
	
`.lineHeightInPixels`, a.k.a. `.size`:

	This is the default way of dictating font size, although it will
	be `None` if you have assigned a value to `.emWidthInPixels`
	instead. It dictates the vertical space allocated to each line of
	text, in pixels (to within a margin of error that depends on the
	sizes that the current font provides). Note that the lines may
	appear to occupy additional space if `.linespacing` is not 1.0

`.linespacing`:

	This dictates where one line of text starts, vertically,
	relative to the next. It is expressed as a proportion of the line
	height. The default value is 1.1, which means there will be
	blank space between lines equal to 10% of the line height. Values
	less than 1.0 may cause lines of text to overlap.

`.string`:

	This is the text string to be rendered. It may contain newline
	characters. It may be a unicode string (however, note that
	special characters will only be rendered correctly to the
	extent that the currently selected `.font` provides them).

`.wrapping`:

	This is `None` by default, which means your `.string` content
	will be rendered unchanged. If you give it a positive integer,
	then your `.string` will be re-wrapped to the specified number
	of pixels, with a ragged edge.  If you give it a negative
	integer, then similarly the wrapped width in pixels is equal
	to the magnitude of that integer, but now the text is left-
	and right-justified to remove the ragged edge.  Paragraph
	breaks are retained, as are whitespace characters that indent
	the beginning of each paragraph. A paragraph break can be
	indicated by a blank line, or indeed by a newline character
	that is immediately followed by *any* additional whitespace.

`.border`:

	This dictates the thickness of the border around the text. It
	can be a scalar (in which case it is considered to be a
	proportion of the text size) or it can be a pair of numbers
	(in which case it is interpreted as horizontal and vertical
	thickness in pixels).

`.padto`:

	This is `None` by default, indicating that the resulting texture
	image should occupy the minimal space necessary to satisfy the
	other parameters.  However, you can use this property to
	guarantee a larger minimum size, in pixels. Supply either a
	single integer (to create a square image) or a pair of integers
	indicating width and height. 

`.align`:

	Set this to `'left'`, `'right'` or `'center'` to dictate the way
	in which multiple lines of the same text image are aligned
	relative to each other.
	
`.fill`:
	
	This can be a single number in the range 0 to 1, or it can be a
	sequence of three or four such numbers specifying an RGB or RGBA
	color that is used for the text. By default, the text is white
	(1.0) which means that the text color can also be controlled as
	expected by the `.color` property of the `Stimulus` instance
	itself.

`.bg`:
	
	This can be a single number in the range 0 to 1, or it can be a
	sequence of three or four such numbers specifying an RGB or RGBA
	color that is used fill the background of each line of text.
	This includes the `.border`, but does not include space beyond the
	end of shorter lines, nor does it include space between lines that
	results from `.linespacing` values greater than 1. By default, the
	background is fully transparent.
	
`.blockbg`:
	
	This can be a single number in the range 0 to 1, or it can be a
	sequence of three or four such numbers specifying an RGB or RGBA
	color that is used fill the background of the entire image. If
	`.bg` is also specified, then it can be used to manipulate
	independently the background color of the text lines themselves,
	superimposed on the `.blockbg` color. By default, the background
	is fully transparent.
	
"""
__all__ = [
]
import os
import re
import sys
import ast
import inspect
import warnings
import collections

from . import Location; from .Location import PackagePath
from . import DependencyManagement; from .DependencyManagement import Import, Require
from . import Dependencies; from .Dependencies import numpy, Image, ImageDraw, ImageFont
Require( 'numpy', 'ImageDraw', 'ImageFont' )
matplotlib = Import( 'matplotlib' )

# home-made 'six'-esque stuff:
try: apply
except NameError: apply = lambda x: x()
try: FileNotFoundError
except NameError: FileNotFoundError = IOError
if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )
def IfStringThenRawString( x ):    return x.encode( 'utf-8' ) if isinstance( x, unicode ) else x
def IfStringThenNormalString( x ):
	if str is not bytes and isinstance( x, bytes ): return x.decode( 'utf-8' )
	if str is not unicode and isinstance( x, unicode ): return x.encode( 'utf-8' )
	return x

FONTS = []
STYLES = set()

TEST = """\
1: In Xanadu did Kubla Khan
2: A stately pleasure-dome decree:
3: Where Alph, the sacred river, ran
4: Through caverns measureless to man
5: Down to a sunless sea.""" # Samuel Taylor Coleridge (1816): Kubla Khan

TEST_WRAPPING = """\
The problem is, or rather one of the problems, for
there are many, a sizeable proportion of which are
continually clogging up the civil, commercial, and
criminal courts in all areas of the Galaxy, and
especially, where possible, the more corrupt ones,
this.

The previous sentence makes sense. That is not the
problem. This is:

	Change.

Read it through again and you'll get it.


 -	Douglas Adams
	So Long And Thanks For All The Fish (1984)"""

TEST_PANGRAM = """\
pack my box with five dozen liquor jugs
THOSE FIVE BOXING WIZARDS JUMP QUICKLY!"""

def Raw2Unicode( t ):  # works around a particularly annoying Python 2 <-> 3 wrinkle
	try: t = t.encode( 'raw_unicode_escape' )
	except: pass
	return t.decode( 'utf-8' )
TEST_UNICODE = Raw2Unicode( "\xE0\xA4\xAE\xE0\xA4\xA8\xE0\xA5\x8B\xE0\xA4\xBD\xE0\xA4\xB9\xE0\xA4\xAE\xE0\xA4\xB8\xE0\xA5\x8D\xE0\xA4\xAE\xE0\xA4\xBF\x20\xE0\xA4\xB5\xE0\xA4\xBE\xE0\xA4\x95\xE0\xA5\x8D\xE0\xA4\xA4\xE0\xA5\x8D\xE0\xA4\xB5\xE0\xA4\xAE\xE0\xA5\x8D\x20\xE0\xA5\xA4\x0A\xE0\xA4\xB8\xE0\xA4\xBE\xE0\xA4\xAE\xE0\xA4\xBE\xE0\xA4\xB9\xE0\xA4\xAE\xE0\xA4\xB8\xE0\xA5\x8D\xE0\xA4\xAE\xE0\xA4\xBF\x20\xE0\xA4\x8B\xE0\xA4\x95\xE0\xA5\x83\xE0\xA4\xA4\xE0\xA5\x8D\xE0\xA4\xB5\xE0\xA4\xAE\xE0\xA5\x8D\x20\xE0\xA5\xA4" )


if matplotlib:
	import matplotlib.font_manager, matplotlib.ft2font
	class Font( object ):
		def __init__( self, filename ):
			filename = IfStringThenNormalString( filename )
			self.filename = filename.replace( '\\', '/' )
			try: ft2obj = matplotlib.ft2font.FT2Font( self.filename )
			except RuntimeError: self.good = False; return
			else: self.good = True
			self.family_name = ft2obj.family_name
			self.style = sorted( word for word in ft2obj.style_name.lower().split() if word != 'regular' )
			try: self.monospace = len( { ft2obj.load_char( ord( char ) ).horiAdvance for char in 'iM' } ) == 1
			except: self.monospace = False
			self.words = self.family_name.lower().split() + self.style
			if self.monospace: self.words += [ 'mono', 'monospace', 'monospaced' ]
			self.italic = 'italic' in self.style
			self.bold = 'bold' in self.style
		description = property( lambda self: '"' + self.family_name + '" ' + ' '.join( self.style ).title() + ( ' (monospace)' if self.monospace else '' ) )
		short_description = property( lambda self: self.family_name + ' '.join( self.style ).title() )
		def __repr__( self ): return '%s(%r)' % ( self.__class__.__name__, self.filename )
		def __str__( self ): return self.description
	fonts = [ Font( filename ) for filename in matplotlib.font_manager.findSystemFonts() ]
	fonts = { ( f.description + ' ' + repr( f.filename ) ).lower() : f for f in fonts if f.good }
	FONTS[ : ] = sorted( fonts.values(), key=lambda f: f.description )
	STYLES = { s for f in FONTS for s in f.style }
else:
	warnings.warn( 'failed to find installed system fonts (%s)' % matplotlib )

def IdentifyFont( name, styles=None ):
	if isinstance( name, ( tuple, list ) ):
		for eachName in name:
			result = IdentifyFont( eachName )
			if result is not None: return result
		return None
	name = getattr( name, 'filename', name )
	if os.path.isfile( name ): return name
	newname = PackagePath( 'fonts', name )
	if os.path.isfile( name + '.ttf' ): name += '.ttf'
	elif os.path.isfile( newname ): name = newname
	elif os.path.isfile( newname + '.ttf' ): name = newname + '.ttf'
	if os.path.isfile( name ): return name
	words = name.lower().split()
	if words and words[ -1 ] == 'regular': words = words[ :-1 ]
	elif styles: words += list( styles )
	candidates = [ f for f in FONTS if all( word in f.words for word in words ) ]
	candidates.sort( key=lambda f: len( f.short_description ) )
	if candidates: return candidates[ 0 ]
	return None

PROBE_NOMINAL_LINE_HEIGHT = 'Th_`'
PROBE_FULL_LINE_HEIGHT    = 'Th_`qy'

def LoadFont( name='monaco', emWidthInPixels=None, lineHeightInPixels=None ):
	
	if not ImageFont:
		warnings.warn( 'failed to load font: %s\n' % ImageFont )
		return None
	
	name = IdentifyFont( name )
	name = getattr( name, 'filename', name )	
	if name is None: return None
	
	if emWidthInPixels is None and lineHeightInPixels is None:
		raise ValueError( 'must supply either emWidthInPixels or lineHeightInPixels' )
	if emWidthInPixels is not None and lineHeightInPixels is not None:
		raise ValueError( 'must supply either emWidthInPixels or lineHeightInPixels, but not both' )		
	font_size = 1
	while True:
		font = ImageFont.truetype( name, font_size ) # NB: names for installed ttf fonts are abbreviated and for some reason CASE SENSITIVE even on Windows
		if emWidthInPixels is not None and font.getsize( 'm' )[ 0 ] >= emWidthInPixels: break
		if lineHeightInPixels is not None and font.getsize( PROBE_NOMINAL_LINE_HEIGHT )[ 1 ] >= lineHeightInPixels: break
		font_size += 1
	return font

def GetTextSizeSafely( func, string, **kwargs ):
	if string: string = string.strip( '\n' )
	x, y = func( string if string else ' ', **kwargs )
	if not string: x = 0
	return x, y
	
def RenderTextOntoImage( imageNumpy, position, string, border=( 0, 0 ), linespacing=1.1, align='left', anchor='lower left', bg=None, blockbg=None, defer=False, wrapping=None, **kwargs ):
	
	kwargs.setdefault( 'fill',  ( 255, 255, 255 ) )
	font = kwargs.get( 'font', None )
	anchor = anchor.lower()
	align = align.lower()
	
	base = imageNumpy
	if base is None: base = numpy.zeros( [ 2, 2, 3 ], 'uint8' )
	imagePIL = Image.fromarray( base[:2,:2,:] )
	draw = ImageDraw.Draw( imagePIL )
	# draw.multiline_text and draw.multiline_textsize may not exist, depending on your version of PIL / pillow
	lineHeight = GetTextSizeSafely( draw.textsize, PROBE_NOMINAL_LINE_HEIGHT, font=font )[ 1 ]
	fullLineHeight = GetTextSizeSafely( draw.textsize, PROBE_FULL_LINE_HEIGHT, font=font )[ 1 ]
	
	if not border: border = 0
	if isinstance( border, ( int, float ) ): border = [ int( round( border * lineHeight * 0.45 ) ) ] # the 0.45 is black magic
	if len( border ) == 1: border *= 2
	
	if not wrapping: wrapping = 0 # handles None
	string = WrapString( string,
		wrapWidth = abs( wrapping ),
		spacesPerTab = 4,
		widthFunc=lambda s: GetTextSizeSafely( draw.textsize, s, font=font )[ 0 ],
		justify = wrapping < 0,
		leftAligned = ( align == 'left' ),
	)
	lines = string.split( '\n' ) # BLANKNESS
	nlines = len( lines )
	if nlines < 2: linespacing = 1
	lineStride = lineHeight * linespacing
	widths, heights = zip( *[ GetTextSizeSafely( draw.textsize, line, font=font ) for line in lines ] )
	heights = [ max( height, fullLineHeight ) for height in heights ]
	bbwidth = max( widths ) + 2 * border[ 0 ]
	bbheight = lineStride * len( lines ) + 2 * border[ 1 ]
	if 'left' in align: xs = [ 0 for width in widths ]
	elif 'right' in align: xs = [ bbwidth - width - 2 * border[ 0 ] for width in widths ]
	else: xs = [ 0.5 * ( bbwidth - width ) - border[ 0 ] for width in widths ]
	xs = numpy.array( xs, float ) + position[ 0 ] + border[ 0 ]
	ys = numpy.array( [ i * lineStride for i in range( nlines ) ], float ) + position[ 1 ] + border[ 1 ] - ( fullLineHeight - lineHeight ) / 2.0
	if 'left' in anchor: pass
	elif 'right' in anchor: xs -= bbwidth
	else: xs -= 0.5 * bbwidth
	if 'top' in anchor or 'upper' in anchor: pass
	elif 'bottom' in anchor or 'lower' in anchor: ys -= lineStride * nlines
	else: ys -= bbheight / 2.0
	# the xs and ys are now bottom-left coordinates for each line
	xs = numpy.round( xs ).astype( int )
	ys = numpy.round( ys ).astype( int )
	primitives = []
	for x, y, width, height, line in zip( xs, ys, widths, heights, lines ):
		primitives.append( dict(
			command='text',
			kwargs=dict( xy=[ x, y ], text=line, **kwargs ),
			bgfill=bg,
			bbox=[ x - border[ 0 ], y - border[ 1 ], x + width + border[ 0 ], y + height + border[ 1 ] ],
		) )
	if defer: return primitives
	else: return DeferredDraw( imageNumpy, primitives, blockbg=blockbg )
	
def MakeTextImage( string='Hello World', position=( 0, 0 ), imageNumpy=None, anchor='upper left', align='center', **kwargs ):
	
	kwargs = dict( kwargs )
	for key in 'fill bg blockbg'.split():
		value = kwargs.get( key, None )
		if isinstance( value, ( int, float ) ): value = [ value ] * 3
		if value: kwargs[ key ] = tuple( [ max( 0, min( 255, int( round( 255.0 * x ) ) ) ) for x in value ] )
	
	if string is None: string = '' # BLANKNESS
	try: string = str( string )     # converts non-basestring objects to str
	except UnicodeEncodeError: pass # fails on unicode objects under Python 2, but that's OK - we can use the unicode object directly
	if 'font' not in kwargs: kwargs[ 'font' ] = LoadFont( kwargs.pop( 'font_name', 'monaco' ), kwargs.pop( 'font_size', 30 ) )
	kwargs.update( dict( imageNumpy=imageNumpy, position=position, string=string, anchor=anchor, align=align, defer=True ) )
	padto = kwargs.pop( 'padto', None )
	primitives = RenderTextOntoImage( **kwargs )
	shift = None
	if padto is not None:
		try: padto[ 0 ]
		except: padto = [ padto ]
		paddedWidth, paddedHeight = padto[ 0 ], padto[ -1 ]
		renderedBBox, _ = ComputeBoundingBox( primitives, shift=None )
		renderedWidth  = renderedBBox[ 2 ] - renderedBBox[ 0 ]
		renderedHeight = renderedBBox[ 3 ] - renderedBBox[ 1 ]
		shift = max( 0, int( ( paddedWidth - renderedWidth ) / 2 ) ), max( 0, int( ( paddedHeight - renderedHeight ) / 2 ) )
		primitives.insert( 0, dict( command=None, kwargs={}, bbox=[ -shift[ 0 ], -shift[ 1 ], paddedWidth - shift[ 0 ], paddedHeight - shift[ 1 ] ] ) )
	if imageNumpy is None:
		bbox, _ = ComputeBoundingBox( primitives, shift=shift )
		width, height = bbox[ 2: ] # ignore negative coordinate space
		#height, width = numpy.vstack( [ primitive[ 'bbox' ][ 3:1:-1 ] for primitive in primitives ] ).max( axis=0 )
		bg = kwargs.get( 'fill', None )
		if bg is None: bg = ( 255, 255, 255 )
		bg = ( list( bg ) * 4 )[ :4 ]
		bg[ -1 ] = 0
		bg = numpy.array( [ [ bg ] ], dtype='uint8' )
		kwargs[ 'imageNumpy' ] = imageNumpy = numpy.tile( bg, [ height, width, 1 ] )
	bbox = DeferredDraw( imageNumpy, primitives, blockbg=kwargs.get( 'blockbg', None ), shift=shift )
	return imageNumpy

def ComputeBoundingBox( primitives, shift=None ):
	if not shift: shift = 0
	try: xshift, yshift = shift[ 0 ], shift[ -1 ]
	except: xshift = yshift = shift
	bbox = [ 0, 0, 0, 0 ]
	coords = [ d[ 'bbox'] for d in primitives if 'bbox' in d ]
	if coords:
		xstart, ystart, xstop, ystop = zip( *coords )
		bbox = [
			int( max( 0, min( xstart ) + xshift ) ),
			int( max( 0, min( ystart ) + yshift ) ),
			int( max( xstop ) + xshift ),
			int( max( ystop ) + yshift ),
		]
	return bbox, ( xshift, yshift )

def DeferredDraw( imageNumpy, primitives, blockbg=None, shift=None ):
	imagePIL = Image.fromarray( imageNumpy )
	draw = ImageDraw.Draw( imagePIL )
	bbox, ( xshift, yshift ) = ComputeBoundingBox( primitives, shift=shift )
	if blockbg == True: blockbg = ( [ d[ 'bgfill' ] for d in primitives if d.get( 'bgfill', None ) ] + [ None ] )[ 0 ] 
	if blockbg: draw.rectangle( xy=bbox, fill=blockbg )
	for d in primitives:
		fill = d.get( 'bgfill', None )
		xy = d.get( 'bbox', None )
		if fill and xy:
			if xy[ 3 ] <= xy[ 1 ] or xy[ 2 ] <= xy[ 0 ]: continue # BLANKNESS
			draw.rectangle( xy=[ coord + delta for coord, delta in zip( xy, [ xshift, yshift, xshift, yshift ] ) ], fill=fill )
	for d in primitives:
		kwargs = d[ 'kwargs' ]
		if 'xy' in kwargs: kwargs[ 'xy' ] = [ coord + delta for coord, delta in zip( kwargs[ 'xy' ], [ xshift, yshift, xshift, yshift ] ) ]
		if d[ 'command' ] == 'text' and not d[ 'kwargs' ].get( 'text', None ): continue # BLANKNESS
		if d[ 'command' ]: getattr( draw, d[ 'command' ] )( **d[ 'kwargs' ] )
	if imageNumpy.size: imageNumpy.flat = numpy.array( imagePIL ).flat # BLANKNESS
	return bbox  # if you expand this as (xstart, ystart, xstop, ystop) then the relevant slice of the image is imageNumpy[ xstart:xstop, ystart:ystop, : ]

def WrapString( s, wrapWidth=80, spacesPerTab=4, widthFunc=len, justify=True, leftAligned=True ):
	spaceWidth = float( widthFunc( ' ' ) )
	tabWidth = spaceWidth * spacesPerTab
	if not wrapWidth or wrapWidth < 0:
		if tabWidth > 0 and '\t' in s:
			lines = s.split( '\n' )
			for iLine, line in enumerate( lines ):
				pieces = line.split( '\t' )
				width = 0
				for iPiece, piece in enumerate( pieces ):
					pieceWidth = widthFunc( piece )
					if iPiece:
						targetWidth = width + tabWidth
						targetWidth -= targetWidth % tabWidth
						extraSpaces = int( round( ( targetWidth - width ) / spaceWidth ) )
						pieces[ iPiece ] = ' ' * extraSpaces + piece
						pieceWidth += spaceWidth * extraSpaces
					width += pieceWidth
				lines[ iLine ] = ''.join( pieces )
			s = '\n'.join( lines )
		return s
	
	paragraphs = re.split( r'\n(?=\s+)', s )
	for iPara, s in enumerate( paragraphs ):
		s = re.sub( r'(\S)\s*\n\s*', r'\1 ', s )
		words = re.split( r'(\s*\S+)', s )[ 1::2 ]
		width = 0
		extraSpaces = [ 0 ]
		lines = [ '' ]
		for i, word in enumerate( words ):
			if width == 0 and not leftAligned: word = word.lstrip( ' \t' )
			targetWidth = width
			while tabWidth and word.startswith( '\t' ):
				word = word[ 1: ]
				targetWidth += tabWidth
				targetWidth -= targetWidth % tabWidth
			if spaceWidth and targetWidth > width:
				word = ' ' * int( round( ( targetWidth - width ) / spaceWidth ) ) + word
			wordWidth = widthFunc( word )
			if width == 0 or width + wordWidth < wrapWidth:
				width += wordWidth
				lines[ -1 ] += word
			else:
				if justify and spaceWidth:
					extraSpaces[ -1 ] += int( ( wrapWidth - width ) / spaceWidth )
				if i or not leftAligned:
					word = word.lstrip( ' ' )
					wordWidth = widthFunc( word )
				width = wordWidth
				lines.append( word )
				extraSpaces.append( 0 )
		if justify:
			for i, ( nExtra, line ) in enumerate( zip( extraSpaces, lines ) ):
				gapPattern = r'(\S\s+)(\S)'
				_, nGaps = re.subn( gapPattern, '', line )
				nExtra = list( numpy.diff( numpy.round ( numpy.linspace( 0, nExtra, nGaps + 1, endpoint=1 ) ) ).astype( int ) ) 
				lines[ i ] = re.sub( gapPattern, lambda m: m.group( 1 ) + ' ' * nExtra.pop( 0 ) + m.group( 2 ), line )
		paragraphs[ iPara ] = '\n'.join( lines )
	return '\n'.join( paragraphs )

	
from . import Rendering

QUERY = object()

class TextGenerator( Rendering.Scheduled ):
	
	DEFAULTS = dict(
		align = 'left',
		border = ( 0, 0 ),
		linespacing = 1.1,
		fill = ( 1.0, 1.0, 1.0 ),
		bg = None,
		blockbg = None,
	)
	
	stimulus = Rendering.Scheduled.parent  # property
	
	def __init__( self, string=' ', stimulus=None, **kwargs ):
		self.__font_size = ( 'lineheightinpixels', 35 )
		self.__font_family = 'monaco'
		self.__font_styles = set()
		self.__font_found = False
		self.__font_changed = True
		self.__formatting_options = d = dict(
			string = string,
			font = None,
			wrapping = None,
			padto = None,
		)
		d.update( self.DEFAULTS )
		self.__formatting_changed = True
		self.__image_changed = False
		self.Set( **kwargs )
		self.stimulus = stimulus
		
	
	def _Property( self, optionName, newValue=QUERY ):
		opt = optionName.lower().replace( '_', '' )
		if opt in STYLES:
			oldValue = ( opt in self.__font_styles )
			if newValue is QUERY or newValue == oldValue: return oldValue
			if newValue: self.__font_styles.add( opt )
			else: self.__font_styles.remove( opt )
			self.__font_changed = True
		elif opt in [ 'style' ]:
			oldValue = ' '.join( sorted( self.__font_styles ) ).title()
			if not oldValue: oldValue = 'Regular'
			if newValue is QUERY: return oldValue
			if not newValue: newValue = 'Regular'
			newValue = { x for x in newValue.lower().split() if x != 'regular' }
			if self.__font_styles == newValue: return oldValue
			self.__font_styles = newValue
			self.__font_changed = True
		elif opt in [ 'family', 'familyname', 'fontfamily', 'fontname', 'font' ]:
			if hasattr( newValue, 'family_name' ):
				if self.__font_styles != newValue.style:
					self.__font_changed = True
					self.__font_styles = set( newValue.style )
				newValue = newValue.family_name
			oldValue = self.__font_family
			if newValue is QUERY or newValue == oldValue: return oldValue
			if newValue is None: newValue = 'default'
			self.__font_family = newValue
			self.__font_changed = True
		elif opt in [ 'emwidthinpixels', 'lineheightinpixels' ]:
			oldType, oldValue = self.__font_size
			if newValue is QUERY: return oldValue if opt == oldType else None
			if newValue is None: return
			if ( opt, newValue ) == ( oldType, oldValue ): return oldValue
			self.__font_size = ( opt, newValue )
			self.__font_changed = True
		elif opt in self.__formatting_options:
			if opt == 'string' and newValue not in [ None, QUERY ]:
				try: newValue = str( newValue ) # converts non-basestring objects to str
				except UnicodeEncodeError: pass # fails on unicode objects under Python 2, but that's OK - we can use the unicode object directly
				if not newValue: newValue = '' # BLANKNESS
			oldValue = self.__formatting_options[ opt ]
			if newValue is QUERY or newValue == oldValue: return oldValue
			self.__formatting_options[ opt ] = newValue
			self.__formatting_changed = True
	
	def _Update( self ):
		if self.__font_changed:
			self.__font_changed = False
			sizeMode, sizeValue = self.__font_size
			if   sizeMode.startswith( ( 'e', 'w' ) ): sizeMode = 'emWidthInPixels'
			elif sizeMode.startswith( ( 'l', 'h' ) ): sizeMode = 'lineHeightInPixels'
			font = IdentifyFont( self.__font_family, styles=self.__font_styles )
			fname = getattr( font, 'family_name', None )
			if fname is not None: self.__font_family = fname
			style = getattr( font, 'style', None )
			if style is not None: self.__font_styles = set( style )
			self.__font_found = font is not None
			if not self.__font_found: font = 'monaco'
			self.__formatting_options[ 'font' ] = LoadFont( font, **{ sizeMode : sizeValue } )
			self.__formatting_changed = True
		if self.__formatting_changed:
			self.__formatting_changed = False
			self.__image = MakeTextImage( **self.__formatting_options )
			self.__image_changed = True
		if not self.__image_changed: return
		stimulus, world = self.stimulus, self.world
		if stimulus is None or world is None: return
		stimulus.LoadTexture( self.__image, True )
		self.__image_changed = False
	
	@property
	def font_found( self ): return self.__font_found

for name in STYLES:
	if len( name ) > 3 and name[ 0 ] not in '0123456789':
		TextGenerator._MakeProperty( name )	
TextGenerator._MakeProperty( 'family', 'family_name', 'font', 'font_family', 'font_name' )
TextGenerator._MakeProperty( 'emWidthInPixels', 'em' )
TextGenerator._MakeProperty( 'lineHeightInPixels', 'size' )
TextGenerator._MakeProperty( 'string' )
TextGenerator._MakeProperty( 'style' )
TextGenerator._MakeProperty( 'wrapping' )
TextGenerator._MakeProperty( 'padto' )
for name in TextGenerator.DEFAULTS:
	TextGenerator._MakeProperty( name )

TextGenerator._AttachAsProperty( Rendering.Stimulus, 'text', 'string',
	#onRemove = lambda host, guest: host.LoadTexture( [ [] ] ),
	# if we comment out onRemove, then `s.text = None` freezes the last-rendered texture, but removes the `TextGenerator` and its regularly scheduled update call
	# Since we might conceivably want to freeze textures, we'll leave it like this, especially now that `sample.text=''` behaves sensibly
)
