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
This optional sub-module supports devices by Cambridge Research
Systems Ltd.  It requires the third-party package `pyserial`.

The main purpose is to set the mode of a "Bits#" stimulus
generator, as follows::

    from Shady.CRS import BitsSharp
    bs = BitsSharp( serialPortName, mode='monoPlusPlus', world=world )
    with bs:
        # ...

If you want to change modes in mid-experiment you can call
`bs.SetMode()`, and if you want to send other commands you
can use `bs.SendCommand()`.  To receive a reply, use
`bs.Receive()`.

If you pass your `Shady.World` instance as the `world` constructor
argument, then the `BitsSharp` object will automatically perform
the appropriate `.SetBitCombiningMode()` calls when the hardware
mode is changed.
"""

__all__ = [
	'BitsSharp',
]

import time
import weakref

try: from . import DependencyManagement
except ImportError: import serial
else: serial = DependencyManagement.Import( 'serial' )

class SerialDevice( serial.Serial ):
	
	DEFAULT = object()
	COMMAND_PREFIXES = ( '', )
	COMMAND_SUFFIXES = ( '\n', )
	DEFAULT_WAIT = 0
	DEFAULT_TIMEOUT = None
	
	def __init__( self, *pargs, **kwargs ):
		self.verbose = kwargs.pop( 'verbose', False )
		kwargs.setdefault( 'timeout', self.DEFAULT_TIMEOUT )
		super( SerialDevice, self ).__init__( *pargs, **kwargs )
			
	def SendCommand( self, cmd, receive=True, prefix=DEFAULT, suffix=DEFAULT, verbose=DEFAULT ):
		if prefix is self.DEFAULT: prefix = self.COMMAND_PREFIXES[ 0 ]
		if suffix is self.DEFAULT: suffix = self.COMMAND_SUFFIXES[ 0 ]
		possible_prefixes = self.COMMAND_PREFIXES if prefix in self.COMMAND_PREFIXES else ( prefix, )
		possible_suffixes = self.COMMAND_SUFFIXES if suffix in self.COMMAND_SUFFIXES else ( suffix, )
		if prefix and not cmd.startswith( possible_prefixes ): cmd = prefix + cmd
		if suffix and not cmd.endswith(   possible_suffixes ): cmd = cmd + suffix
		cmd = cmd.encode( 'utf-8' )
		if verbose is self.DEFAULT: verbose = self.verbose
		if verbose: print( 'sending %r to %s' % ( cmd, self.port ) )
		self.write( cmd )
		if receive: return self.Receive()
	
	def Receive( self, wait=DEFAULT, timeout=DEFAULT, binary=False ):
		if wait is self.DEFAULT: wait = self.DEFAULT_WAIT
		if wait: time.sleep( wait )
		if timeout is not self.DEFAULT: timeout, self.timeout = self.timeout, timeout
		msg = self.read() + self.read_all()
		if timeout is not self.DEFAULT: timeout, self.timeout = self.timeout, timeout
		if not binary and not isinstance( msg, str ):
			try: msg = msg.decode( 'utf-8' )
			except UnicodeDecodeError: pass
		return msg
		
class BitsSharp( SerialDevice ):
	"""
	The `BitsSharp` class inherits from `serial.Serial`.  As such, it will 
	opens a serial-port connection when constructed, and can optionally be
	used as a context manager in a `with` clause, such that `.close()` gets
	called automatically whenever and however you exit from the clause::
	
	    w = Shady.World()
	    bs = BitsSharp( serialPortName, mode='monoPlusPlus', world=w )
	    with bs:
	        s = w.Sine( pp=0, sigf=0.01, size=400, contrast=0.04, bg=0.1)
	        w.Run()  # or whatever else you want to do

	Note that we have added two additional (optional) construction arguments:
	`mode` and `world`.  If you supply `world`, then the `.bitCombiningMode` of
	that `Shady.World` instance will automatically be updated to keep pace with
	whichever mode you select. Mode selection can happen at construction time
	with the `mode` argument, or in subsequent calls to `bs.SetMode()`.

	The `Shady.World` class has transparent support for both the `'monoPlusPlus'`
	and `'colourPlusPlus'` modes.  With other modes, you're on your own as
	regards hacking the correct rendering.
	
	Other Bits# commands (see the Bits# technical manual) can be sent with the
	`.SendCommand()` method.  You can omit the initial `$` or `#` and the
	trailing `\r` if you want. For example::
	
	    bs.SendCommand( 'TemporalDithering=ON' )
	    # lets the on-board processor of the Bits# handle the dithering
	
	Note that the Bits# device will only be available for serial connections
	if "CDC" mode is turned on in its firmware configuration: if you have
	access to the Bits# as a USB mass-storage device, ensure that the first
	few lines of its `\Firmware\Config.xml` file are configured to enable
	CDC mode and disable other modes (including mass-storage mode itself)::
	
	    <Entry USB_MSD="OFF" />
	    <Entry USB_CDC="ON" />
	    <Entry USB_HID="OFF" />
	
	and then power-cycle it (pull out the power cord, put it back in, wait).
	The converse operation (i.e. to turn mass-storage mode back on temporarily
	until the next power-cycle) can be done by closing an existing connection
	with::
	
	    bs.close( convertToMassStorage=True )
	
	
	"""
	
	COMMAND_PREFIXES = ( '$', '#', )
	COMMAND_SUFFIXES = ( '\r', )
	DEFAULT_WAIT    = 0.010
	DEFAULT_TIMEOUT = 0.100
	
	def __init__( self, *pargs, **kwargs ):
		self.__mode = None
		self.__world = None
		mode = kwargs.pop( 'mode', None )
		world = kwargs.pop( 'world', None )
		if world: self.__world = weakref.ref( world )
		super( BitsSharp, self ).__init__( *pargs, **kwargs )
		self.SetMode( mode )
	
	def __exit__( self, *pargs ):
		# TODO: revert back to previous mode
		return super( BitsSharp, self ).__exit__( *pargs )
	
	MODES = { alias : canonical for canonical, aliases in dict(
		colourPlusPlus = 'colourPlusPlus colour++ colorPlusPlus color++ C48 C42 2',
		monoPlusPlus   = 'monoPlusPlus mono++ M16 M14 1',
		bitsPlusPlus   = 'bitsPlusPlus bits++',
		autoPlusPlus   = 'autoPlusPlus auto++',
		# is there really no standard (C24) mode?
	).items() for alias in aliases.lower().split() }	
	
	def SetMode( self, mode ):
		if mode is not None:
			if isinstance( mode, ( int, float ) ): mode = str( int( mode ) )
			canonicalName = self.MODES.get( mode.lower(), None )
			if canonicalName: self.__mode = canonicalName
			else: raise ValueError( 'unrecognized mode %r' % mode )
			world = self.world
			if world: world.SetBitCombiningMode( self.__mode )
			self.SendCommand( self.__mode, receive=False )
		return self
	mode = property( fget=lambda self: self.__mode, fset=lambda self, value: self.SetMode( value ) )

	@property
	def world( self ): return self.__world() if self.__world else None
	@world.setter
	def world( self, w ): self.__world = weakref.ref( w )
	
	def close( self, convertToMassStorage=False ):
		"""
		Close the serial connection.
		
		If `convertToMassStorage` is True, the command `USB_massStorage`
		is sent immediately before closing. This causes the Bits# to stop
		acting as a serial device altogether, and start acting as a USB
		file storage device. This lets you re-configure the Bits# (for
		example, by loading gamma-correction information). Once you do
		this, you will not be able to reconnect to over the serial port
		interface until you have rebooted the device (unplug and re-plug
		its power cable).
		"""
		if convertToMassStorage: self.SendCommand( 'USB_massStorage', receive=False )
		super( BitsSharp, self ).close()
