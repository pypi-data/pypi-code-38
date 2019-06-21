"""
... module:: qsdn
	:platform: Unix, Windows
	:synopsis:  This module allows for parsing, validation and production of numeric literals, written with thousand separators through out the number.  Often underlying system libraries for working with locales neglect to put thousand separators (commas) after the decimal place or they sometimes use scientific notation.  The classes inherit from the Qt classes for making things less complex.
	
	Thousand separators in general will not always be commas but instead will be different according to the locale settings.  In Windows for example, the user can set his thousand separator to any character.  Support for converting strings directly to Decimals and from Decimals to strings is included.
	
	Also, numbers are always expressed in standard decimal notation.
		
	Care has been taken to overload all of the members in a way
	that is consistent with the base class QLocale and QValidator.
	
	This module requires PyQt5.  It is presently only tested with Microsoft Windows.  Users from other platforms are invited to join my team and submit pull-requests to ensure correct functioning.  If KDE and PyKDE are installed on your system, KDE's settings for thousands separator and decimal symbol will be used.  Otherwise
	the system's locale settings will be used to determine these values.
"""

# Class inheritance diagram
#					  
#		   [[QLocale]]
#				^
#				|
#				|
#		  [[Locale]]
#	  

# Class inheritance diagram
#		 
#		 [[QValidator]]		  
#				^			   
#				|			   
#				|			   
#	  [[NumericValidator]]
#				^			   
#               |
#               |
# [[LimitingNumericValidator]] 
# 
# SDN stands for 'standard decimal notation'.  That is not 'normalized Scientific notation'.

import re
import traceback, sys
from decimal import Decimal as D
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# KDE: a walled garden.
# This is supposed to work with or without KDE.

# Style note:
# You might be wondering why I didn't make a class for KDE's locale in
# order to avoid assigning methods. The goal of Locale is to provide
# a drop in replacement for QLocale. A KDELocale if implemented as a
# separate class, would require the user to handle KDE as a special
# case. In order to comply with drop in replacement requirement, the
# user shall see only one locale subclass from here. Trying to use a
# hidden subclass with setDefault meant we needed a flag, and to assign
# to methods anyway.
try:
	from PyKDE4.kdecore import KGlobal
	def _make_KDE(locale):
		locale.decimalPoint = KGlobal.locale().decimalSymbol
		locale.groupSeparator = KGlobal.locale().thousandsSeparator
except:
	# "** Could not load KDE: Falling back to QT only."
	def _make_KDE(locale):
		  pass

### Pass a numeric string of a positive number (without sign) and add commas where approriate
def add_commas(locale, st):
	# first eliminate the commas
	i = 0
	while i < len(st):
		if st[i] == locale.groupSeparator():
			if i < pos:
				pos -= 1
			st = st[:i] + st[i+1:]
		else:
			i = i + 1	
	if (locale.numberOptions() & QLocale.OmitGroupSeparator) != QLocale.OmitGroupSeparator:
		dpl = (st.find(locale.decimalPoint()) + len(st) + 1) % (len(st) + 1)
	else:
		return st
	i = dpl+4
	while i < len(st):
		if st[i] != locale.groupSeparator():
			st = st[:i] + locale.groupSeparator() + st[i:]
		i += 4
	i = dpl-3
	while i > 0 and st[i] != ' ':
		if st[i] != locale.groupSeparator():
			st = st[:i] + locale.groupSeparator() + st[i:]		
		i -= 3
	return st


class Locale(QLocale) :
	""" 
		
	For a Locale, locale:
		Main benefit is numbers converted to a string are always converted to standard decimal notation.  And you control how far numbers are written before they are truncated.  Another benefit is it works with decimal.Decimal numbers natively.  So
		numbers get converted directly from String to Decimal and vice versa.
		
	    To construct one, you can supply a name of a locale and specify the mandatory and maximum digits after the decimal point.
	    
	    locale = Locale("en_US", 2, 3)
	    locale.toString(4) is '4.00'
	    locale.toString(4.01) is '4.01'
	    locale.toString(1/3) is '0.333'
	    
	    To specify the language and script, pass in a QLocale to the constructor: like this:
	    qlocale  = QLocale('en_US', QLocale.Latin, QLocale.Spanish)
	    sdnlocale = Locale(qlocale, 2, 3)
	
	
		To get the Decimal of a string, s, use:
		
		(d, ok) = locale.toDecimal(s, 10)
		
		The value d is your decimal, and you should check ok before you trust d.
		
		To get the string representation use:
		
		s = locale.toString(d)
	   
	    All to* routines take a string, and an optional base.  If the base is set to zero, it will look at the first digits of the number to determine 
	    base it should use.  So, '013' will be interpreted as 11 (as 0 indicates octal form) unless you set the base to 10, in which as it will be interpreted as 13.
	    You can use '0x' to prefix hexadecimal numbers.  Some developers don't want to expose this programming concept to the users of thier software.  For those
	    who don't specify the base explicitly as 10.  As of 1.0.0, the base defaults to 10, because the new behavior as of PyQt5 in the QLocale class is to always 
	    have the base fixed as 10.
	    
		By default Locale will use the settings specified in your default locale.  This is guaranteed to be true for Mac OS, Windows and KDE-GUIs.  
		 
		
		
	"""
	_default_KDE = True	
	_default_locale = QLocale.system()
	_country     = None
	_name        = None
	
	# p_mandatory_decimals becomes _mandatory_decimals
	# p_maximum_decimals becomes _maximum_decimals
	# they control the behavior of toString
	def __init__(self, _name = None, p_mandatory_decimals = D(0), p_maximum_decimals = D('Infinity')) :
		"""Control how many decimal places are put for units other than Decimal.
		
		Args:
		  name (str) the name of the locale: example: "en_US"
		
		  p_mandatory_decimals (int or Decimal) the mandatory decimal places required for a number
		  
		  p_maximum_decimals (int or Decimal) the maximum number of decimals required for a number
		"""
	
		#print("Locale constructor called with: %r, %r, %r, %r" % (self, _name, p_mandatory_decimals, p_maximum_decimals))
		if _name is not None:
			if _name.__class__ == QLocale or _name.__class__ == Locale:
				QLocale.__init__(self, _name.language(), _name.script(), _name.country() )
			else:
				QLocale.__init__(self, _name)
		else:
			# default is broken in underlying QLocale, implement it here.
			if Locale._default_locale is None:
				Locale._default_locale = QLocale.system()
			d = Locale._default_locale
			#print("Default locale has name: %s" %(d.name(),)) 
			Locale.__init__(self, d)
			# Pull default parameters from KDE if available.
			_make_KDE(self)
		self._mandatory_decimals = p_mandatory_decimals
		self._maximum_decimals = p_maximum_decimals
	#	#print("Resulting Locale has name %r" % (self.name(),))

				
	def _toNumber(self, s, base, zero):
		"""This creates a decimal representation of s.
			 
			 It returns an ordered pair.  The first of the pair is the Decimal number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the decimal returned.
			 
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
		  
		   Like the other to* functions of QLocale as well as this class Locale, interpret a 
		   a string and parse it and return a Decimal.  The base value is used to determine what base to use.
		   
		   If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		   be interpreted as hexadecimal and '777' will be interpreted as a decimal.  It is done this way
		   so this works like toLong, toInt, toFloat, etc...
		   Leading and trailing whitespace is ignored.
		"""
		debug_mode = False
		if debug_mode:
			if base is None:
				print('toDecimal(%s, None)' % (s,))
			else:
				print('toDecimal(%s, %d)' % (s, base,))
		polarity = 1
		comma = self.groupSeparator()
		point = self.decimalPoint()
		# derive the base if not set above.
		# here a copy is made, the original s will not be
		# modified.
		s = s.strip()
		if s.startswith(self.negativeSign()):
			polarity = -1
			s = s[len(self.negativeSign()):]
		if base == 0:
			if s.casefold().startswith('0x'):
				return polarity * self._toNumber(s[2:], 16, zero)
			elif s.startswith('0'):
				return polarity * self._toNumber(s[1:], 8, zero)
			else:
				return polarity * self._toNumber(s, 10, zero)
		# seemingly pointless, the code below
		# avoids issues where two variables point to the same data
		v = zero + zero
		shift = zero - zero
		
		are_there_digits = False
		add_shifts = False
		comma_offset = None
		for c in s:
			if c == comma:
				if comma_offset == None:
					comma_offset = 0
				elif base == 10 and comma_offset != 3:
					return (1, False)
				elif self.numberOptions() & QLocale.RejectGroupSeparator == QLocale.RejectGroupSeparator:
					return (2, False)
				comma_offset = 0
			elif c == point:
				comma_offset = 0
				if add_shifts:
					# two decimal point characters is bad
					if debug_mode:
						print("Returning bad for double .")
					return (polarity * v/base**shift, False)
				add_shifts = True
			else:
				to_add = ord(c) - ord(self.zeroDigit())
				if to_add < 0 or to_add >= 10:
					to_add = "abcdef".find(c)
					if to_add != -1:
						to_add += 10
				if to_add == -1:
					to_add = "ABCDEF".find(c)
					if to_add != -1:
						to_add += 10
				if to_add >= 0 and to_add < 16:
					are_there_digits = True
					v *= base
					v += to_add
					if comma_offset != None:
						comma_offset += 1
					if add_shifts:
						shift += 1
				else:
					if debug_mode:
						print("Returning bad for illegal character %s .", (c,))
					return (polarity * v / base**shift, False)
		v /= base ** shift
		v *= polarity
		return (v, are_there_digits)
		
	def toDecimal(self, s, *, base = 10):
		"""This creates a decimal representation of s.
			 
			 It returns an ordered pair.  The first of the pair is the Decimal number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the decimal returned.
			 
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.

        Like the other to* functions of QLocale as well as this class Locale, interpret a 
		a string and parse it and return a Decimal.  The base value is used to determine what base to use.
		It is done this way
		so this works like toLong, toInt, toFloat, etc...
		Leading and trailing whitespace is ignored.
		"""
		return self._toNumber(s, base, D(0))

	def toString(self, x, arg2 = None, arg3 = None):
		"""	Convert any given Decimal, double, Date, Time, int or long to a string.
	
		Numbers are always converted to Standard decimal notation.  That is to say,
		numbers are never converted to scientifc notation.
		
		The way toString is controlled:
		If passing a decimal.Decimal typed value, the precision is recorded in the 
		number itself.  So, D('4.00') will be expressed as '4.00' and not '4'.
		D('4') will be expressed as '4'.
		
		When a number passed is NOT a Decimal, numbers are created in the following way:
		Two extra parameters, set during creation of the locale, determines how 
		many digits will appear in the result of toString().
		For example, we have a number like 5.1 and mandatory decimals was set	
		to 2, toString(5.1) should return '5.10'.  A number like 6 would be '6.00'.
		A number like 5.104 would depend on the maximum decimals setting, also 
		set at construction of the locale:
		_maximum_decimals controls the maximum number of decimals after the decimal point
		So, if _maximum_decimals is 6 and _mandatory_decimals is 2 then 
		toString(3.1415929) is '3.141,592'.
		Notice the number is truncated and not rounded.  
		Consider rounding a copy of the number before displaying.
		"""
		  
		try:
			xt = D(x).as_tuple()
		except:
			return QLocale.toString(self, x, arg2, arg3)
		self.zeroDigit()
		digit_map = [chr(ord(self.zeroDigit()) + a) for a  in [0,1,2,3,4,5,6,7,8,9]] 
		st = ''.join(digit_map[a] for a in xt.digits)
		if -xt.exponent < len(st):
			# The decimal point must go to the right of the most significant digit.
			if xt.exponent < 0:					
				# the decimal point goes next to a digit we already have
				st = st[:len(st)+xt.exponent] + self.decimalPoint() + st[len(st)+xt.exponent:]
			else:
				# We need to add digits before we can write a decimal point
				# but if you don't have all of the digits for this.
				# Standard notation is always used here.
				# For example:
				# An expression like 3e2 becomes '300' even though, it is 
				# understood that such a value is not as precise as D(300). 
				st = st + digit_map[0] * xt.exponent					
		else:
			# the digits all belong to places right of the decimal point. 
			st = (digit_map[0]) + str(self.decimalPoint()) + (digit_map[0]) * (-xt.exponent-len(st)) + st
		dpl = st.find(self.decimalPoint())
		if x.__class__ != D:
			if dpl == -1 and self._mandatory_decimals:
				st += (self.decimalPoint() + digit_map[0] * (self._mandatory_decimals))
			if dpl != -1 and len(st) - dpl - 1 < self._mandatory_decimals:
				st += (digit_map[0] * (self._mandatory_decimals - len(st) + dpl + 1))
			if dpl != -1 and len(st) - dpl - 1 > self._maximum_decimals:
				st.truncate(dpl+self._maximum_decimals+1)
			if dpl != -1:
				while st.endswith(str(self.zeroDigit())) and len(st)-dpl-1 > self._mandatory_decimals:
					st.chop(1)
		st = add_commas(self, st)
		if xt.sign == 1:
			st = self.negativeSign() + st
		return st
					
	@staticmethod				
	def system() :
		""" Returns the system default for Locale.  
		"""		
		return Locale(QLocale.system())
	
	@staticmethod
	def c() :
		""" Returns the C locale.  In the C locale, to* routines will not accept group separtors and do not produce them. 
		"""
		_c = Locale(QLocale.c())
		return _c
		
	@staticmethod
	def setDefault(new_default):
		_default_locale = new_default
		try:
			Locale._default_KDE = (new_default.decimalPoint == KGlobal.locale().decimalSymbol)
		except:
			Locale._default_KDE = False
	
	# return a double represented by the string s.
	def toDouble(self, s, *, base = 10):
			""" Parses the string s and returns a floating point value whose string is s.
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
			 
			  It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
			  """
			return str(self._toNumber(s, base, 0.0))
			
	# return a float represented by the string s.
	def toFloat(self, s, *, base = 10):
		""" Parses the string s and returns a floating point value whose string is s.
		 
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
		  """
		(ans, good) = self._toNumber(s, base, 0.0)
		if good and float(ans) == ans:
			return (ans, True)
		else:
			return (ans, False)

			
	# return a int represented by the string s.
	def toInt(self, s, *, base = 10):
		""" Parses the string s and returns an integer value whose string is s.
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
		"""
		(ans, good) = self._toNumber(s, base, 0)
		if good and int(ans) == ans:
			return (ans, True)
		else:
			return (ans, False)
		return self._toNumber(s, base, int(0))
   
	# return a long represented by the string s.
	def toLongLong(self, s, *, base = 10):
		""" Parses the string s and returns a floating point value whose string is s.
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
		
		Leading and trailing whitespace is ignored.		""" 
		return self._toNumber(s, base, 0)
		
	def toShort(self, s, *, base = 10):
		""" Parses the string s and returns a short value whose string is s.
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
		
		Leading and trailing whitespace is ignored.		"""
		(ans, good) = self.toInt(s, base = base)
		if good and -32768 <= ans <= 32767:
			return (ans, True)
		else:
			return (ans, False)
		
	# return a uint represented by the string s.
	def toUInt(self, s, *, base = 10):
		""" Parses the string s and returns an unsigned integer value whose string is s.
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base (which defaults to 10), so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
		
		Leading and trailing whitespace is ignored.		""" 
		(ans, good) = self._toNumber(s, base, 0)
		if good and 0 <= ans < 4294967296:
			return (ans,True)
		else:
			return (ans,False)

	# return a ulonglong represented by the string s.
	def toULongLong(self, s, base = 10):
		""" Parses the string s and returns an unsigned long long value whose string is s.
		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.

		
		Leading and trailing whitespace is ignored.		""" 
		(ans, good) = self._toNumber(s, base, 0)
		if good and 0 <= ans < 9223372036854775808:
			return (ans,True)
		else:
			return (ans,False)
		
	# return a ushort represented by the string s.
	def toUShort(self, s, base = 10):
		""" Parses the string s and returns a unsigned long long value whose string is s.

		
		It returns an ordered pair.  The first of the pair is the number, the second of the pair indicates whether the string had a valid representation of that number.  You should always check the second of the ordered pair before using the number returned.
		
			 :note:
				 You may set another parameter, the base, so you can interpret the string as 8 for octal, 16 for hex, 2 for binary.
		  
							   
		If base is set to 0, numbers such as '0777' will be interpreted as octal.  The string '0x33' will
		be interpreted as hexadecimal and '777' will be interpreted as a decimal.
		
		Leading and trailing whitespace is ignored.		""" 
		(ans, good) = self._toNumber(s, base, 0)
		if good and 0 <= ans < 65336:
			return (ans,True)
		else:
			return (ans,False)
			
	def mandatoryDecimals(self):
		return self._mandatory_decimals
		
	def maximumDecimals(self):
		return self._maximum_decimals

	def __eq__(self, other):
		if other.__class__ is not Locale:
			return False
		return QLocale.__eq__(self, other) and self._mandatory_decimals == other._mandatory_decimals and self._maximum_decimals == other._maximum_decimals

class NumericValidator(QValidator) :
	""" NumericValidator allows for numbers of any length but groupSeparators are added or corrected when missing or out of place.
																							  
	  U.S. dollar amounts;
						 dollar = NumericValidator(6,2)
						 s = '42.1'
						 dollar.validate(s='42.1', 2)   =>  s = '42.10'
						 s='50000'
						 dollar.toString(s)			  => s = ' 50,000.00'
	"""																							  
	localeSet = pyqtSignal( Locale )

	def __init__(self, parent = None) :
		QValidator.__init__(self, parent)
		self._locale = None
		self.setLocale( Locale() )
	
	def validate(self, s, pos):
		debug = False
		if debug:
			print("Running for -.42")
		
		sign_str = ''
		if not s.startswith(self._locale.negativeSign()):
			if debug:
				print("not a neg sign?")
			return self.validate_positive(s, pos)
		
		sign_str = self._locale.negativeSign()
		if len(s) == 1:
			if debug:
				print("deemed intermediate")
			return QValidator.Intermediate, s, pos
				
		if pos == 0:
			if debug:
				print("delegated to validate_positive without pos")
			(status, s, throw_away) =  self.validate_positive(s[1:], 0)
			return (status, sign_str+s, 0)
		
		if debug:
			print("delegated to validate_positive with pos")
		(status, s, pos) = self.validate_positive(s[1:], pos-1)
		return (status, sign_str+s, pos+1)	
		
	def validate_positive(self, s, pos):
		try:
			if s == "debugparty":
				debug = True
			debug             = False
			old_s             = s
			i                 = 0
			digits_count      = 0
			if debug:
				print('starting validate()')
			zero_code         = ord(self._locale.zeroDigit())
			dp                = s.find(self._locale.decimalPoint())
	
			if debug:
				print("\t\tInside validator checking if %s is empty" % (s,))
	
			if len(s) == 0:
				return QValidator.Intermediate, s, 0
	
			tail_comma    = (s[-1] == self._locale.groupSeparator())
	
			if not (0 <= pos <= len(s)):
				return QValidator.Invalid, s, pos
	
			comma_after_cursor_pos = pos > 0 and s[pos-1] == self._locale.groupSeparator()
	
			if dp == 0:
				s = self._locale.zeroDigit() + s
				dp += 1
				if pos > 0:
					pos += 1
			
			if dp == -1:
				dp = len(s)
			elif s[dp+1:].find(self._locale.decimalPoint()) != -1:
				return QValidator.Invalid, s, pos
				
			if debug:
				print("\t\tLeading zero added if needed to %s" % (s,))
			# drop commas
			
			i = 0
			while i < len(s) and i < pos:
				if s[i] == self._locale.groupSeparator():
					s = s[:i] + s[i+1:]
					pos -= 1
					if i < dp:
						dp = dp - 1
				else:
					i = i + 1
			
			while i < len(s):
				if s[i] == self._locale.groupSeparator():
					s = s[:i] + s[i+1:]		
					if i < dp:
						dp = dp - 1
				else:
					i = i + 1
			if debug:
				print("\t\tInside validator commas dropped %s" % (s,))
	
	
			# drop leading zeroes unless the decimal point character is right after it.
			while len(s) > 1 and s[0] == self._locale.zeroDigit() and s[1]!= self._locale.decimalPoint():
				s = s[1:]
			
			
			
			# add commas back in
			i = dp - 1
			while i > 0:
				if (1+dp-i) % 4 == 0:
					s = s[:i] + self._locale.groupSeparator() + s[i:]
					if i < pos:
						pos += 1
					dp = dp + 1
				i = i - 1
			
			i = dp + 1
			while i < len(s):
				if (i-dp) % 4 == 0:
					s = s[:i] + self._locale.groupSeparator() + s[i:]
					if i < pos:
						pos += 1
				i = i + 1
			
			if old_s == s:
				s = old_s
			
			if comma_after_cursor_pos and (pos == len(s) or s[pos] == self._locale.groupSeparator()):
				pos += 1
				
			if debug:
				print("\t\tInside validator commas added back in %s" % (s,))
				
			if tail_comma:
				s += self._locale.groupSeparator()
			
			if debug:
				print("\t\tReturning if last character is a comma %s" % (s,))
			if tail_comma:
				return QValidator.Intermediate, s, pos
			
			if debug:
				print("\t\tInside validator checking invalid characters %s" % (s,))
			while i < pos and i < len(s):
				if  0 <= ord(s[i]) - zero_code < 10:
					digits_count += 1
				elif not (s[i] == self._locale.groupSeparator()
				or s[i] == self._locale.decimalPoint()):
					return QValidator.Invalid, s, pos
				i = i + 1
			
			return QValidator.Acceptable, s, pos
		except RecursionError as rerr:
			traceback.print_exc(file=sys.stdout)
			return QValidator.Invalid, s, pos
		finally:
			if debug:
				print("leaving validate()")
	
	def setLocale(self, plocale):
		""" Set the locale used by this Validator.  
		"""
		if plocale != self._locale:
			self.localeSet.emit(plocale)
		self._locale = plocale

	def locale(self):
		""" get the locale used by this validator 
		"""
		return self._locale

class NumberOutOfRange(Exception):
	pass

class NumberTooSmall(NumberOutOfRange):
	pass

class NumberTooBig(NumberOutOfRange):
	pass

class LimitingNumericValidator(NumericValidator) :
	""" NumericValidator limits the number of digits after the decimal
	 point and the number of digits before. 
	 
	  bitcoin						 :  NumericValidator(8, 8)
	  US dollars less than $1,000,000 :  NumericValidator(6, 2)
	  
	  
	  If use space is true, spaces are added on the left such that the location
	  of decimal point remains constant.  Numbers like '10,000.004', '102.126' become 
	  aligned.
	  Bitcoin amounts:
	  
						 '		0.004,3'
						 '	   10.4'
						 '	  320.0'
						 '		0.000,004'
																							  
	  U.S. dollar amounts;  
						 dollar = NumericValidator(6,2)
						 s = '42.1'
						 dollar.validate(s='42.1', 2)   =>  s = '	 42.10'
						 s='50000'
						 dollar.toString(s)			  => s = ' 50,000.00'
			   
								
	"""																							  
	
	bang = pyqtSignal( )

	
	def __init__(self, maximum_decamals = 1000, maximum_decimals = 1000, use_space = False, parent = None) :
		QValidator.__init__(self, parent)
		# true if we use spaces for justifying the string.
		#create signal
		self.numeric_only_validator = NumericValidator(parent)
		self.spaced = use_space
		self.maximum_decimals = maximum_decimals
		self.maximum_decamals = maximum_decamals
		self.characters_before_decimalPoint = maximum_decamals * 4 // 3
		self.characters_after_decimalPoint = maximum_decimals * 4 // 3
		self._locale = None
		self._debug  = False
		self.setLocale( Locale() )
	
	def decimals(self):
		""" gets the number of decimal digits that are allowed *after* the decimal point """
		return self.characters_after_decimalPoint * 3//4
	
	def setDecimals(self, i):
		""" sets the number of decimal digits that should be allowed **after** the decimal point """
		self.maximum_decimals = i
		self.characters_after_decimalPoint = i * 4 // 3
	
	def decamals(self):
		  """ gets the number of decimal digits that are allowed **before** the decimal point (apart from spaces)"""
		  return self.characters_before_decimalPoint * 3 / 4
		  
	def setDecamals(self, i):
		  """ sets the number of decimal digits that should be allowed **before** the decimal point """
		  self.characters_before_decimalPoint = i * 4 // 3
	
	# Count non-space, non-comma characters: digits and a decimal point up to limit in str s.	
	def _count_occurences(self, s, limit):
		  counter = 0
		  for i in range(0, limit):
			  if s[i]  != (self._locale.groupSeparator()) and s[i] != (' '):
				  counter += 1
		  return counter;

	def _correct_white(self, s, pos):
		# Make it such that the number of characters before the decimal point is self.characters_before_decimalPoint by adding or removing spaces and returning a new position such that this new position will be between the same digits as the position indicated by pos.
		whole_part = QRegExp(str('^ *(' + self._locale.negativeSign() + '?(\d|') + self._locale.groupSeparator() + ')*)')
		whole_part.indexIn(s)
		if self._debug:
			print("Whole part is ", whole_part)
		decimalPoint_location = whole_part.matchedLength()
		assert(decimalPoint_location in range(0, len(s)+1))
		if self.spaced:
			needed_white = max(0, self.characters_before_decimalPoint - len(whole_part.cap(1)))
			pos += self.characters_before_decimalPoint - decimalPoint_location if pos != 0 else 0
		else:
			needed_white = 0
		last_white = -1
		while last_white+1 < len(s):
			if s[last_white + 1] == ' ':
				last_white += 1
			else:
				break
		s = needed_white*' ' + s[last_white+1:]
		dp = s.find(self._locale.decimalPoint())
		if len(s) - (0 if dp == -1 else dp) > self.characters_before_decimalPoint:
			raise NumberTooBig
		
		if (len(s)-dp if dp >= 0 else 0) > self.characters_after_decimalPoint:
			raise NumberTooSmall
			
		return (s, pos)
					 
	def validate(self, s, pos):
		""" Validates s, by adjusting the position of the commas to be in the correct places and adjusting pos accordingly as well as space in order to keep decimal points aligned when varying sized numbers are put one above the other.
		"""
		debug = self._debug
		if debug:
			print('Call to self.validate(%s,%d)' % (s.__repr__(),pos,))
			print((len('Call to self.validate(') + pos) * ' ' + '^')
			print("max decimals: ", self.maximum_decimals)
			print("max chars befor decimal point: ", self.characters_before_decimalPoint)
		try:
			if debug:
				print("H")
			dpl = s.find(self._locale.decimalPoint())
			zero_code = ord(self._locale.zeroDigit())
			if dpl == -1:
				dpl = len(s)
			
			digit_count = 0
			status = None
			if s.find('!') != -1:
				self.bang.emit()
				if debug:
					print('return QValidator.Invalid, %s,%d' % (s.__repr__(),pos,))
				return QValidator.Invalid, s, pos

			# Test to see if there are too many post decimal point digits
			if dpl != len(s):
				if debug:
					print("A")
				for i in range(dpl+1,len(s)):
					c = ord(s[i])
					if 0 <= c - zero_code <= 9:
						if debug:
							print(digit_count)
						digit_count = digit_count + 1
						if digit_count > self.maximum_decimals:
							s = s[:i]
							if pos > i:
								pos = i
							if debug:
								print('return QValidator.Intermediate, %s,%d' % (s.__repr__(),pos,))
							status = QValidator.Intermediate
							break
			# Test to see whether there are too many pre decimal point digits 
			digit_count = 0
			for i in range(0,dpl):
				c = ord(s[i])
				if 0 <= c - zero_code <= 9:
					digit_count = digit_count + 1
					if digit_count > self.maximum_decamals:
						if pos > i and pos < dpl:
							pos = i
						elif pos >= dpl:
							pos = i + (pos - dpl)
						if debug:
							print('return QValidator.Intermediate, %s,%d' % (s.__repr__(),pos,))
						s = s[:i] + s[dpl:]
						if status is None:
							status = QValidator.Intermediate
					
			
			# If the field is just all spaces, return Intermediate
			if debug:
				print("E")
			for x in s:
				if x != ' ':
					break
			else:
				if debug:
					print('return QValidator.Intermediate, %s,%d' % (s.__repr__(),pos,))
				return QValidator.Intermediate, s, pos
				
			# Test to see there is something other than a number in the string
			if not self.improper_decimal_re.exactMatch(s):
				if debug:
					print('return QValidator.Invalid, %s,%d' % (s.__repr__(),pos,))
				return QValidator.Invalid, s, pos
			if debug:
				print("R")
				
				
			# Test to see whether the number is perfectly formed
			if self.proper_re.exactMatch(s):
				if status is not None:
					return status, s, pos
				# no need to fix the commas
				try:
					(s, pos) = self._correct_white(s, pos)
				except:
					pass
				if debug:
					print("E")
				if debug:
					print("s = %s\n" % (s.__repr__(),))
				if debug:
					print('return QValidator.Acceptable, %s,%d' % (repr(s),pos,))
				return QValidator.Acceptable, s, pos
			if debug:
				print(pos)
				print(self.improper_decimal_re.pos(2))
				
			# Validate the numerical part only regardless of spaces
			pos_inside_spaces = pos < self.improper_decimal_re.pos(2)		 
			if debug:
				print("H")
			nstatus = None
			ns = ''
			npos = None
			if pos_inside_spaces:
				if debug:
					print("    Calling number only validate on %s, %d" % (repr(self.improper_decimal_re.cap(2)), 0))
				(nstatus, ns, npos) = self.numeric_only_validator.validate(	self.improper_decimal_re.cap(2), 0 )
				s = self.improper_decimal_re.cap(1) + ns
				if debug:
					print("    Result is %s, %d" % (repr(ns), 0))
			else:
				if debug:
					print("    Calling number only validate on %s, %d" % (repr(self.improper_decimal_re.cap(2)), pos-self.improper_decimal_re.pos(2)))
				(nstatus, ns, npos) = NumericValidator.validate(self, 
					self.improper_decimal_re.cap(2), pos-self.improper_decimal_re.pos(2) )
				if debug:
					print("    Result is %s, %d" % (repr(ns), npos))
				s = self.improper_decimal_re.cap(1) + ns
				pos = npos + self.improper_decimal_re.pos(2)
			
			if status is None:
				status = nstatus
			if debug:
				print('status is %d' % (status,))
			if debug:
				print("E")
			(s, pos) = self._correct_white(s, pos)
			if debug:
				print("space difference is ", len(s) - s.find('.'))

			if debug:
				print("Y")
			if debug:
				if status == QValidator.Acceptable:
					print('return QValidator.Acceptable, %s,%d' % (s.__repr__(),pos,))
				elif status == QValidator.Invalid:
					print('return QValidator.Invalid, %s,%d' % (s.__repr__(),pos,))
				else:
					print('return QValidator.Intermediate, %s,%d' % (s.__repr__(),pos,))
			return status, s, pos
		except NumberOutOfRange:
			if debug:
				print('return QValidator.Intermediate, %s,%d (Number out of range)' % (s.__repr__(),pos,))
			return QValidator.Intermediate, s, pos

	def setLocale(self, plocale):
		""" Set the locale used by this Validator.  
		"""	
		if plocale == self._locale:
			return
		self._locale = plocale
		space_part = ' *' if self.spaced else ''
		decimalPoint = QRegExp.escape(str(self._locale.decimalPoint()))
		groupSeparator = QRegExp.escape(str(self._locale.groupSeparator()))
		negativeSign  = QRegExp.escape(self._locale.negativeSign())
		self.proper_re = QRegExp('^(' + space_part + \
			negativeSign + '?\d{1,3}(' + groupSeparator + '\d{3})*)' \
			'(' + decimalPoint + '((\d{3}' + groupSeparator + ')*\d{1,3})?)?')
		self.improper_decimal_re = QRegExp('^( *)(' + self._locale.negativeSign() \
			+ '?([\d' + groupSeparator + ']*)(' + decimalPoint + '([\d' + groupSeparator + ']*))?)')
		self.localeSet.emit(plocale)
		

	def locale(self):
		""" get the locale used by this validator 
		"""
		return self._locale
