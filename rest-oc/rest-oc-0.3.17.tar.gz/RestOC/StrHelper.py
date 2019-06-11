# coding=utf8
""" StrHelper Module

Several useful helper methods for use with strings
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

# Python imports
from base64 import b64encode, b64decode
from random import randint

# The sets available for the random function
_mdRandomSets = {
	"0x":	"0123456789abcdef",
	"0":	"01234567",
	"10":	"0123456789",
	"10*":  "123456789",
	"az":	"abcdefghijklmnopqrstuvwxyz",
	"az*":	"abcdefghijkmnopqrstuvwxyz",
	"AZ":	"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"AZ*":	"ABCDEFGHJKLMNPQRSTUVWXYZ",
	"aZ":	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"aZ*":	"abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ",
	"!":	"!@#$%^&*-_+.?"
}

def decrypt(key, val):
	"""Decrypt

	Decrypts a string using the key and returns it. Key must be in multiples of
	16 bytes

	Arguments:
		key {str} -- A key that was used to encrypt the original value
		val {str} -- The value to decrypt

	Returns:
		str
	"""

	# Load PyCrypto
	try:
		from Cryptodome.Cipher import AES
	except Exception as e:
		print('%s\n' % str(e))
		return None

	# base64 decode the value; this can explode because of padding errors
	try: val = b64decode(val)
	except TypeError: return None

	# Recreate the IV
	sIV = val[:16]

	# Strip out the IV from the encrypted value
	val = val[16:]

	# Create the cipher and store the decrypted value
	oC = AES.new(key, AES.MODE_CFB, sIV, segment_size=128)

	# Return the decrypted value
	return oC.decrypt(val)

def encrypt(key, val):
	"""Encrypt

	Encrypts a string using the passed key and returns it. Key must be in
	multiples of 16 bytes

	Arguments:
		key {str} -- The key used to encrypt the value
		val {str} -- The value to encrypt and return

	Returns:
		str
	"""

	# Try to load PyCrypto
	try:
		from Crypto import Random
		from Cryptodome.Cipher import AES
	except Exception as e:
		print('%s\n' % str(e))
		return None

	# Generate an IV
	sIV = Random.new().read(AES.block_size)

	# Create a new cipher using the key and the IV
	oC = AES.new(key, AES.MODE_CFB, sIV, segment_size=128)

	# Encrypt the value
	val = oC.encrypt(val)

	# Add the IV
	val = '%s%s' % (sIV, val)

	# Return the entire thing as a base 64 encoded string
	return b64encode(val)

def normalize(val):
	"""Normalize

	Replaces all special alpha characters with their ascii equivalent

	Args:
		val {str} -- The text to normalize

	Returns:
		str
	"""
	return strtr(val, {
		'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A',
		'Æ': 'A', 'Ć': 'C', 'Č': 'C', 'Ç': 'C', 'Đ': 'Dj', 'È': 'E',
		'É': 'E', 'Ê': 'E', 'Ë': 'E', 'Ì': 'I', 'Í': 'I', 'Î': 'I',
		'Ï': 'I', 'Ñ': 'N', 'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O',
		'Ö': 'O', 'Ø': 'O', 'Ŕ': 'R', 'Š': 'S', 'Ù': 'U', 'Ú': 'U',
		'Û': 'U', 'Ü': 'U', 'Ý': 'Y', 'Ž': 'Z',
		'Þ': 'B', 'ß': 'Ss',
		'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
		'æ': 'a', 'ć': 'c', 'č': 'c', 'ç': 'c', 'đ': 'dj', 'è': 'e',
		'é': 'e', 'ê': 'e', 'ë': 'e', 'ì': 'i', 'í': 'i', 'î': 'i',
		'ï': 'i', 'ð': 'o', 'ñ': 'n', 'ò': 'o', 'ó': 'o', 'ô': 'o',
		'õ': 'o', 'ö': 'o', 'ø': 'o', 'ŕ': 'r', 'š': 's', 'ù': 'u',
		'ú': 'u', 'û': 'u', 'ý': 'y', 'ý': 'y', 'ÿ': 'y', 'ž': 'z',
		'þ': 'b'
	})

def random(length = 8, sets='_aZ', duplicates=True):
	"""Random

	Generates a random string. By default this function will generate an 8
	character string using lowercase letters with possible repeating characters

	Arguments:
		length {int} -- Requested length of the password
		sets {str|str[]} -- A list of names from the standard sets, a string
			starting with an underscore representing one named set, or any other
			string to be used as an array of characters to chose from. If you
			want certain characters to have a greater chance of appearing, use
			them more times, e.g. twice the 'A's, "AABC", or three times the
			'B's, "ABBBC". Make sure not to turn off duplicates for this to be
			effective
		duplicates {bool} -- Defaults to True, allowing characters to be used
			more than once

	Sets:
		0x:		0123456789abcdef
		0:		01234567
		10:		0123456789
		az:		abcdefghijklmnopqrstuvwxyz
		az*:	abcdefghijkmnopqrstuvwxyz
		AZ:		ABCDEFGHIJKLMNOPQRSTUVWXYZ
		AZ*:	ABCDEFGHJKLMNPQRSTUVWXYZ
		aZ:		abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
		aZ*:	abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ
		!:		!@#$%^&*-_+.?

	Examples:
		> random(8, '_0x')
		"baadbeef"

	Returns:
		str
	"""

	# If the sets are a list
	if isinstance(sets, list):

		# If there is no count
		if not sets:
			raise ValueError('sets must contain at least one set name')

		# Init the string to be used as the allowed characters
		sChars = ''

		# Go through the list
		for s in sets:

			# If the set doesn't exist
			if s not in _mdRandomSets:
				raise ValueError('%s is not a valid set' % s)

			# Else, add it to the allowed characters
			sChars += _mdRandomSets[s]

	# Else if we have a string
	elif isinstance(sets, str):

		# If it starts with an underscore
		if sets[0] == '_':

			# If the set doesn't exist
			if sets[1:] not in _mdRandomSets:
				raise ValueError('%s is not a valid set for %s' % (sets[1:], sys._getframe().f_code.co_name))

			# Else, set it to the allowed characters
			sChars = _mdRandomSets[sets[1:]]

		# Else, use the string as is
		else:
			sChars = sets

	else:
		raise ValueError('%s is not a valid value for sets argument of %s' % (str(sets), sys._getframe().f_code.co_name))

	# Init the return variable
	sText = '';

	# Count the number of characters we can use
	iCount = len(sChars)

	# Create a [length] of random character
	i = 0
	while i < length:
		sFound = sChars[randint(0, iCount - 1)]
		bDup = sText.find(sFound)

		if duplicates or bDup == -1:
			sText += sFound
			i += 1

	# Return the generated string
	return sText

def strtr(text, table):
	"""String Translate

	Port of PHP strtr (string translate)

	Args:
		text (str): The string to translate
		table (dict): The translation table

	Returns:
		str
	"""
	text = str(text)
	buff = []
	i = 0
	n = len(text)
	while i < n:
		for s, r in table.items():
			if text[i:len(s)+i] == s:
				buff.append(r)
				i += len(s)
				break
		else:
			buff.append(text[i])
			i += 1

	return ''.join(buff)
