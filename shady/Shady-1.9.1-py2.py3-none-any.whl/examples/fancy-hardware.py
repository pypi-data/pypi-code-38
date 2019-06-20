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

#: Demonstration of support for 16-bit mono and 48-bit color modes
"""
Shady was primarily designed to allow psychophysical stimuli to be
rendererd easily on commodity (non-specialist) hardware, with
dynamic range enhancement via "noisy-bit" dithering. However, it
also provides support for the high-dynamic range modes of certain
specialized display devices, such as the Bits# by Cambridge
Research Systems Ltd or the ViewPixx by VPixx Inc. Here we
demonstrate how Shady can render stimuli in these special modes.
"""#.

if __name__ == '__main__':
	
	"""
	Let's get the command-line arguments out the way first
	"""#:
	import Shady
	cmdline = Shady.WorldConstructorCommandLine( canvas=True )
	hardware = cmdline.Option( 'hardware', 'auto', type=str, container=None, doc="examples:  --hardware=ViewPixx  or --hardware=BitsSharp"  )
	cmdline.Help().Finalize()
	
	"""
	Now let's create a World, and a Stimulus:
	"""#:
	w = Shady.World( **cmdline.opts )
	s = w.Stimulus(
		atmosphere = w,
		signalFunction = Shady.SIGFUNC.SinewaveSignal,
		signalAmplitude = 0.5,
		signalFrequency = 0.005,
		plateauProportion = 0,
		envelopeSize = min( w.size ) / 2 - 50,
		normalizedContrast = Shady.Oscillator( 0.2 ) * 0.5 + 0.5,
	)
	# Or more concisely:
	# s = w.Sine(sigf=0.01,pp=0,size=400,contrast=Shady.Oscillator(.2)*.5+.5)
	
	"""
	We'll manipulate a `World` property called `.bitCombiningMode`.
	By default, this is 0, or equivalently 'C24', meaning 24-bit
	color with dithering turned on by default.
	
	Let's set it to 1, also known as 'M16' or `'monoPlusPlus' mode.
	Dithering will be disabled, and stimuli will be monochrome (their
	intensity will be determined only by the red component of the
	signal). Each pixel will be represented as a 16-bit integer with
	the more-significant byte stored in red channel and the less-
	significant byte stored in the green.  This would get reinterpreted
	by the Bits# or ViewPixx hardware, and rendered in 16-bit gray-scale.
	"""#:
	
	w.bitCombiningMode = 'M16'
	
	"""
	We can also set it to 2, a.k.a 'C48' or 'colorPlusPlus' mode.
	Instead of sacrificing color, we now sacrifice resolution. The
	`World` will change its nominal size: it will now be divided
	into half the original number of pixels horizontally and (by
	default) also vertically. The left half of each virtual pixel
	will contain its more-signficiant byte, and the right half will
	contain its less-significant byte. The Bits# or ViewPixx would
	reinterpret this as a 16-bit-per-channel full-color image.
	"""#:
	
	print( '  before: {:4d} x {:4d}'.format( *w.size ) )
	w.bitCombiningMode = 'C48'
	print( '   after: {:4d} x {:4d}'.format( *w.size ) )
	

	"""
	Note that the stimulus got physically larger---not because we
	changed its size in pixels (it's still pixellated at 400 x 400,
	the way it was defined) but because we doubled the linear
	physical extent of what the `World` considers to be a "pixel".
	In real applications, of course you'll set the mode of the
	`World` at the very beginning, and then create stimuli based
	on its de-facto `.size`, and there will be no confusion.
	"""#:
	
	"""
	...no confusion, that is, *unless* you decide that you want to
	take advantage of full vertical resolution. The Bits# and
	ViewPixx only require you to reduce *horizontal* resolution, as
	they combine pairs of horizontally-adjacent pixels in the
	graphics card's frame buffer, to determine the (yoked) intensity
	of the corresponding pair of physical pixels. The hardware does
	not require you to throw away vertical resolution as well, but
	Shady does so by default, so that the "pixels" you work with
	remain square and things remain easy to lay out geometrically.
	
	However, if you want to work with non-square pixels, you can.
	Do you really want to do that?
	"""#:
	
	"""
	Are you sure??
	"""#:
	
	"""
	Well, OK then. But you'll have to make a direct call to the
	method that lies behind the `.bitCombiningMode` property, and
	give it an extra argument:
	"""#:
	
	w.SetBitCombiningMode( 'C48', verticalGrouping=1 )
	# whereas for this mode, the default verticalGrouping value is 2
		
	"""
	So now we have a logically square stimulus that appears
	physically non-square.  Perhaps you would like to make it appear
	square, by doubling the number of pixels at which we sample the
	signal function vertically?
	"""#:
	
	s.height *= 2
	print( 'stimulus: {:4d} x {:4d}'.format( *s.size ) )
	
	"""
	Just remember, you asked for it. Be careful what you do
	with geometric transformations of your stimlui. Notice,
	for example, how with non-square pixels, a simple
	rotation of the carrier function causes a change in
	spatial frequency:
	"""#:
	
	s.carrierRotation = Shady.Integral( 20 )
	
	"""
	...and envelope transformations are even wackier:
	"""#:
	
	s.carrierRotation = 0
	s.envelopeRotation = Shady.Integral( 20 )
	
	"""
	---not that you should be rotating the *envelope* of a
	precisely-computed stimulus anyway, because of the
	interpolation artifacts. But this illustrates the more
	general point about non-square pixels---for laying out
	stimuli, I recommend sacrificing vertical resolution
	for the sake of sanity:
	"""#:
	
	# revert the Stimulus to its previous logically-square shape:
	s.height /= 2

	# make the World's pixels square again, too:
	w.SetBitCombiningMode( 'C48', verticalGrouping=2 )

	# and sit still, for goodness' sake:
	s.envelopeRotation = 0
	
	"""
	Now let's put each mode's rendering under the microscope.
	We'll create a stimulus containing only one logical pixel:
	"""#:
	
	p = w.Stimulus( size=1, color=0.5, anchor=-1, pos=w.Place( -1 ), ditheringDenominator=w )
	
	"""
	We'll write a function that empirically captures, then pretty-
	prints, the frame-buffer representation of that single logical
	pixel:
	"""#:
	def Pixel( *args ):
	
		if args:  # you can pass a single value, or three values R, G, B
			p.color = [ arg / 65535.0 for arg in args ]
			
		image = p.Capture( normalize=False ) # We say normalize=False
		# here because otherwise, when w.bitCombiningMode is > 0, the
		# default behavior of .Capture() would be to re-combine the image
		# bytes and return an image of the correct logical size, with
		# high-dynamic-range pixel values in the range 0 to 1. But in
		# this demo, we actually want to see the raw uncombined bytes.

		PrettyPrint( args, image ) # we defined this function out of
		# sight, because the details are unimportant/distracting.
	
	""#>
	def PrettyPrint( args, image ):		
		if not args:
			args = [ x * 65535.0 for x in p.color ]
			if len( set( args ) ) == 1:
				args = args[ :1 ]
		try:
			import numpy
		except ImportError:
			s = ', '.join( '%3d' % x for x in image )
			labels = ''
		else:
			s = '\n'.join(
				'    [    %s    ],' % '  ,  '.join(
					'[ %s ]' % ', '.join(
						'%3d' % channel
						for channel in pixel )
					for pixel in row )
				for row in image )
			labels = '#   ' + '       R    G    B    A    ' * image.shape[ 1 ]
		mode = w.bitCombiningMode
		modeInfo = 'w.bitCombiningMode = %r%s' % ( { 0 : 'C24', 1 : 'M16', 2 : 'C48' }.get( mode, mode ),  '' if mode else ' (dithering on)' if p.ditheringDenominator > 0 else ' (dithering off)' )
		if mode >= 2 and w.pixelGrouping[ 1 ] < 2: modeInfo += ' (but with verticalGrouping=%r)' % w.pixelGrouping[ 1 ]
		s = '\n%s\nPixel( %s ) --> [\n%s\n]%s\n' % ( modeInfo, ', '.join( '%g' % arg for arg in args ), s, labels )
		print( s )
	
	"""
	Let's see that representation in all the different modes.
	
	In regular C24 mode you'll see dithering (so the exact
	byte values might be different each time you capture):
	"""#:
	w.SetBitCombiningMode( 0 )
	Pixel()
	Pixel()
	Pixel()
	"""
	In the other modes dithering is turned off, and pixel
	intensities are just rounded to the nearest 1/65535.
	Here is 16-bit mono mode:
	"""#:
	w.SetBitCombiningMode( 1 )
	Pixel()	
	"""
	Here is 48-bit color mode with non-square pixels:
	"""#:
	w.SetBitCombiningMode( 2, verticalGrouping=1 )
	Pixel()
	"""
	...and here is 48-bit color mode with square pixels:
	"""#:
	w.SetBitCombiningMode( 2, verticalGrouping=2 )
	Pixel()
	
	"""
	As usual, target intensities are expressed, in `p.color`,
	as floating-point numbers from 0 to 1.  However, note that
	we wrote our little ad-hoc diagnostic function `Pixel()`
	such that we can express a new color in 65535ths. So,
	for example:
	"""#:
	
	Pixel( 65534.5 )    # should round up to 65535 = 0xFFFF = (255,255)
	Pixel( 65534.49 ) # should round down to 65534 = 0xFFFE = (255,254)
	
	Pixel( 0, 32767.5, 65535 )  # r, g, b
	
	"""
	Why not try a few examples yourself, in different modes?
	"""#:
	
	"""
	Sometimes you will want to perform gamma-correction using the
	hardware's own built-in method. For this reason, we've set
	the default Shady gamma to 1.0 in this demo.  However, you
	can use Shady's built-in gamma-correction in bit-combining
	modes too, if you want:
	"""#:
	
	w.gamma = 2.2  # or, you know, whatever
	
	"""
	Note that this has affected our Gabor patch `s`, which shares
	its "atmosphere" properties (including `.gamma`) with the
	World `w`.  But it has not changed the gamma-correction of
	our single-pixel test stimulus `p`, because we have not linked
	its `.gamma` to the World in that way:
	"""#:
	
	Pixel( 32767.5 ) # still ends up in the middle of the range
	
	"""
	We will leave you in 24-bit color mode, with a low-contrast
	grating on a low-luminance background.  This stimulus makes
	it relatively easy to see quantization artifacts (especially
	around the edges) when dithering is turned off. We'll also
	install an event-handler that lets you toggle dithering on
	and off by pressing `d` on the keyboard.
	"""#:
	
	w.Set( gamma=1, ditheringDenominator=0, bitCombiningMode=0 )
	s.Set( bg=0.1, contrast=0.04 )
	# Assuming 8-bit DACs, bg=0.1 at gamma=1 leads to a
	# background target level of 25.5: the tiniest amount below
	# that will round to 25, and the tiniest amount above will
	# round to 26.
	
	@w.EventHandler( slot=-1 )
	def ToggleDithering( self, event ):
		if event >> "kp[d]":
			# press d to toggle dithering on or off
			# (NB: only turns on in C24 mode)
			self.ditheringDenominator = 0 if self.ditheringDenominator else self.dacMax
		
	"""
	The final thing to cover is how to use Python to send the
	appropriate mode-setting signals to the hardware.  The
	manufacturer may already supply Python bindings for this
	purpose. We have written some bindings of our own for Shady,
	although due to limitations on access to hardware, we are less
	likely to be able to maintain them than the respective
	manufacturers. But if you want to try ours out, you can import
	machine-specific classes from Shady's optional manufacturer-
	specific submodules.
	
	If you're running this demo on such a device, let's try it.
	If you have such a device connected but are currently running
	this demo on the wrong screen, you should at this point type
	`exit()` and then re-start the demo but with the appropriate
	`--screen` number specified on the command line---for example:
	
	    python -m Shady demo fancy-hardware --screen=2
	
	"""#:
	
	"""
	First let's install another event-handler, in a different
	slot from the dithering toggle.  Once we've set up the
	`device` instance in the next step, this handler will allow
	you to switch between modes with the keyboard, by pressing
	0, 1, 2, or shift+2:
	"""#:
	
	device = None	
	@w.EventHandler( slot=-2 )
	def ChangeDeviceAndWorldMode( self, event ):
		if device and event >> "kp[0]": 
			# press 0 for 24-bit color mode without dithering
			self.ditheringDenominator = 0
			try: device.mode = 'C24'
			except RuntimeError as err: print( err )
			except ValueError as err: print( err ) # because BitsSharp does not recognize this mode
			
		if device and event >> "kp[1]":
			# press 1 for 16-bit mono mode
			try: device.mode = 'M16'
			except RuntimeError as err: print( err )
			
		if device and event >> "kp[2]":
			# press 2 for 48-bit color mode
			# (or shift+2 if you really want to see anisometric 48-bit mode)
			try: device.mode = 'C48'
			except RuntimeError as err: print( err )
			if 'shift' in event.modifiers:
				self.SetBitCombiningMode( 'C48', verticalGrouping=1 )
				
	""#>
	def wrapInput( prompt ):
		try: func = raw_input   # dammit, Guido
		except: func = input
		try: response = func( prompt ).strip()
		except EOFError: response = ''
		print( '' )
		return response
	
	try: _SHADY_CONSOLE_INTERACT
	except NameError:
		if hardware == 'auto': hardware = 'None'; print( 'No --hardware was specified.' )
	else:
		if hardware != 'auto': print( 'You specified --hardware=%s' % hardware )

	if hardware == 'auto':
		"""
		Are you running this demo on a ViewPixx or similar display
		by VPixx, Inc.?
		
		Is it connected to this computer via USB?

		Are the appropriate drivers installed?
		"""#>
		if wrapInput( "Use VPixx device? y/[n]: " ).lower().startswith( 'y' ):
			hardware = 'ViewPixx'
		""#>
		
	if hardware == 'auto':
		"""
		Are you running this demo through a Bits# or similar stimulus
		generator by CRS Ltd.?
		
		Is it connected to this computer via USB?
		
		Are the appropriate drivers installed and do you know the
		serial port address?
		
		Have you installed the third-party python package `pyserial`?
		"""#>
		if wrapInput( "Use CRS device? y/[n]: " ).lower().startswith( 'y' ):
			hardware = 'BitsSharp'
		""#>
		
	if hardware.lower() in [ 'vpixx', 'viewpixx', 'datapixx' ]:
		"OK, let's set it up:"#:
		from Shady.VPixx import ViewPixx
		device = ViewPixx( w )
		""#>
	elif hardware.lower() in [ 'crs', 'bits#', 'bits++', 'display++', 'bitssharp', 'bitsplusplus', 'displayplusplus' ]:
		"Which serial port is it on?"#>
		serialAddress = wrapInput( "Enter serial port address (e.g. COM19 or /dev/tty.usbmodem14111 ): " )
		"OK, let's set it up:"#:
		from Shady.CRS import BitsSharp # NB: this will fail if pyserial isn't installed
		device = BitsSharp( serialAddress, world=w )
		""#>
	elif hardware.lower() not in [ 'none', 'auto' ]:
		print( '\nUnrecognized hardware %r' % hardware )
		""#>
		
	w.ditheringDenominator = 0
	if device:
		print( 'Created %r' % device )
	else:
		"""
		Alrighty then, come back when you have set up your device.
		"""#>
		@w.EventHandler( slot=-2 ) # equivalent to the handler above, but without the device
		def ChangeModeEvenWithoutHardware( self, event ):
			event >> "kp[0]" and self.Set( bitCombiningMode=0, ditheringDenominator=0 )
			event >> "kp[1]" and self.SetBitCombiningMode( 1 )
			event >> "kp[2]" and self.SetBitCombiningMode( 2, verticalGrouping=1 if 'shift' in event.modifiers else 2 )	
		""#>

	print( """
Use the keyboard (0, 1, 2, shift+2) to change mode.
Press d to toggle dithering on/off in mode 0 (24-bit color).
Note the effect on the quantization artifacts.
""" )
	
	""#>
	Shady.AutoFinish( w ) # tidying up in case we didn't get here via `python -m Shady`
