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

#: How to manipulate text stimuli
"""
This demo provides a keyboard-interactive exploration of
Shady's text-rendering capabilities.

It requires third-party packages:  `numpy`, `pillow` and
will fail without them.  Also, `matplotlib` is needed to
access the system's fonts: without it, you will only be
able to render in the "monaco" font.

NB: changing the string content, or font style, of a
    text Stimulus causes the image to be re-rendered on
    the CPU and then transferred from CPU to GPU. This
    is less efficient than Shady normally aims to be,
    and can impact performance, so it's best to ensure
	it does not happen frequently in timing-critical
	applications (see the `showcase` demo for more
	details).
"""#.
if __name__ == '__main__':

	"""
	Parse command-line options:
	"""#:
	import Shady
	cmdline = Shady.WorldConstructorCommandLine()
	cmdline.Help().Finalize()

	"""
	Enable text rendering by explicitly importing `Shady.Text`,
	then create a `World`:
	"""#:
	import Shady.Text  # necessary to enable text/font-handling functionality
	w = Shady.World( **cmdline.opts )

	"""
	Now we'll set up a list of test texts, a list of fonts,
	and a general-purpose function for cycling through them.
	"""#:
	TEXTS = [ Shady.Text.TEST, Shady.Text.TEST_UNICODE, Shady.Text.TEST_WRAPPING, Shady.Text.TEST_PANGRAM ]
	FONTS = list( Shady.Text.FONTS )
	WRAPPING_MODES = [ -800, 800, None ]
	def Cycle( lst, backwards=False ):
		if backwards: lst.insert( 0, lst.pop( -1 ) )
		else: lst.append( lst.pop( 0 ) )
		return lst[ -1 ]
	firstSampleText = Cycle( TEXTS )

	"""
	Creating a text stimulus is as easy as:
	"""#:
	sample = w.Stimulus( text=firstSampleText )
	
	"""
	We assigned a string to the `.text` property. In fact,
	that's a shorthand: what it implicitly does is ensure
	creation of an appropriate text-handling object in
	`sample.text`, and then set *its* property
	`sample.text.string` equal to the desired string.
	
	The `.text` property of a `Stimulus` supports dynamic
	assignment. Let's demonstrate by creating an informative
	caption below our text sample:
	"""#:
	def ReportFont( t ):
		if not sample.text: return ''
		return '{font} ({style}){warning}'.format(
			font = sample.text.font, 
			style = sample.text.style, 
			warning = '' if sample.text.font_found else '\nnot available',
		)
	
	caption = w.Stimulus(
		text = ReportFont, # dynamic-enabled shortcut to .text.string
		xy = lambda t: sample.Place( 0, -1 ) - [ 0, 30 ], # wherever the sample goes or however it grows,
		anchor = ( 0, 1 ),                                # let the top edge of the caption remain 30
		                                                  # pixels below the sample's bottom edge
	)
	caption.text.align = 'center'
	caption.text.blockbg = ( 0, 0, 0, 0.5 )
	caption.text.border = 2

	"""
	Let's set up a pixel ruler for judging the size of the
	finished sample:
	"""#:
	pixelruler = Shady.PixelRuler( 1000, world=w ).Set(
		alpha = 0.7,
		carrierTranslation = lambda t: sample.Place( Shady.LOWER_LEFT, worldCoordinates=False ),
	)
	
	"""
	...but for now, let's hide it:
	"""#:
	pixelruler.visible = False
	
	"""
	Let's set up an event-handler to allow exploration of
	various text properties using keystroke commands:
	"""#:
	@w.EventHandler
	def KeyboardControl( world, event ):
		if event.type in [ 'key_press', 'key_auto' ]:
			# When you get an event.type in [ 'key_press', 'key_release', 'key_auto' ]
			# the key information is to be found in event.key:
			# - event.key allows easy case-insensitive matching (it's always lower case);
			# - non-printing keystrokes (e.g. 'escape', 'up', 'down') are reported;
			# - have to be careful what you assume about international keyboard layouts
			#   e.g. the condition `event.key == '8' and 'shift' in event.modifiers`
			#   guarantees the '*' symbol on English layouts but not on many others;
			# - when the key is held down, you get one 'key_press' followed by multiple
			#   repeating 'key_auto' events.
			command = event.key
			if   command in [ 'q', 'escape' ]: world.Close()
			elif command in [ 'up'   ]: sample.text.linespacing *= 1.1
			elif command in [ 'down' ]: sample.text.linespacing /= 1.1

		if event.type == 'text':
			# Detect a event.type == 'text' and examine event.text:
			# - case sensitive;
			# - non-printing keystrokes cannot be detected;
			# - independent of keyboard layout (you get whatever symbol the user intended to type);
			# - 'text' events are re-issued on auto-repeat when the key is held down.
			command = event.text.lower()
			if   command in [ 'c' ]: sample.text.align = 'center'
			elif command in [ 'l' ]: sample.text.align = 'left'
			elif command in [ 'r' ]: sample.text.align = 'right'
			elif command in [ 'm' ]: sample.text.font = 'monaco'
			elif command in [ 'd' ]: sample.text.font = [ 'arial unicode', 'devanagari', 'nirmala' ] # whichever matches first
			elif command in [ 'f' ] and FONTS: sample.text.font = Cycle( FONTS, 'shift' in event.modifiers )
			elif command in [ 'b' ]: sample.text.bold = not sample.text.bold
			elif command in [ 'i' ]: sample.text.italic = not sample.text.italic
			elif command in [ 't' ]: sample.text = Cycle( TEXTS )  # this is a shorthand - could also say sample.text.string = Cycle( TEXTS )
			elif command in [ '-' ]:      sample.text.size /= 1.1  # .size is an alias for .lineHeightInPixels, so these lines will fail if
			elif command in [ '+', '=' ]: sample.text.size *= 1.1  # text size has most recently been controlled via .emWidthInPixels instead
			elif command in [ 'g' ]: sample.text.blockbg = None if sample.text.blockbg else ( 0, 0.7, 0 )
			elif command in [ 'y' ]: sample.text.bg = None if sample.text.bg else ( 0.7, 0.7, 0 )
			elif command in [ 'w' ]: sample.text.wrapping = Cycle( WRAPPING_MODES )
			elif command in [ 'p' ]: pixelruler.visible = not pixelruler.visible
			elif command in [ '[', ']' ]:
				direction = -1 if command in [ '[' ] else +1
				value = sample.text.border  # could be a scalar (proportion of line height) or tuple of absolute pixel widths (horizontal, vertical)
				try: len( value )
				except: sample.text.border = max( 0, value + direction * 0.1 )
				else:   sample.text.border = [ max( 0, pixels + direction * 10 ) for pixels in value ]
	"""
	That was quite a lot to take in.  So, let's render a legend
	that summarizes the possible keystrokes:
	"""#:
	
	instructions = """
  L / C / R   left / center / right alignment
F / shift+F   cycle through system fonts
      B / I   toggle .text.bold / .text.italic where possible
          M   set .text.font = 'monaco'  (our default font)
          T   cycle between demo texts
          D   try to find a Devanagari font, for the Sanskrit 
      - / +   increase / decrease .text.size
      [ / ]   increase / decrease .text.border
  up / down   increase / decrease .text.linespacing
          Y   toggle yellow .text.bg
          G   toggle green  .text.blockbg
          W   cycle .text.wrapping modes
          P   toggle visibility of the pixel ruler
 Q / escape   close window
"""
	legend = w.Stimulus(
		text = instructions.strip( '\n' ),
		z = +0.5,		
		anchor = ( -1, -1 ),             # Place the lower-left corner of this stimulus...
		xy = w.Place( -1, -1 ) ,         # ...in the lower-left corner of the world.
		text_size = 20,                  #} These are shortcuts to the sub-properties of
		text_border = 2,                 #} `legend.text`, addressed *after* the Stimulus
		text_blockbg = ( 0, 0, 0, 0.5 ), #} is created
	)
	""#>
	print( instructions )
	Shady.AutoFinish( w ) # in case we didn't get here from `python -m Shady ...`
