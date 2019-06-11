# coding=utf8
"""Image

Module to manipulate images and photos, requires the Python Pillow library
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2016-11-11"

# Python imports
import re
from io import StringIO

# Pip Imports
from PIL import Image as Pillow, ImageFile as PillowFile
PillowFile.LOAD_TRUNCATED_IMAGES = True

# Framework imports
from . import Resize

# exif rotation tag
ORIENTATION_TAG = 0x0112

# Regex for valid dimension strings
DIMENSIONS_REGEX = re.compile(r'^(?:[1-9]\d+)?x(?:[1-9]\d+)?$')

# Rotation sequences based on exif orientation flag
__mlSequences = [
	[],
	[Pillow.FLIP_LEFT_RIGHT],
	[Pillow.ROTATE_180],
	[Pillow.FLIP_TOP_BOTTOM],
	[Pillow.FLIP_LEFT_RIGHT, Pillow.ROTATE_90],
	[Pillow.ROTATE_270],
	[Pillow.FLIP_TOP_BOTTOM, Pillow.ROTATE_90],
	[Pillow.ROTATE_90]
]

def apply_rotation(image):
	"""Apply Rotation

	Uses exif data to rotate the image to the proper position

	Arguments:
		image {str} -- A raw image as a string

	Returns:
		str
	"""

	# Load the image into a new StringIO
	sImg = StringIO(image)
	sNewImg = StringIO('')

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# Store the image format
	sFormat = oImg.format

	# Get the proper sequence
	try:
		lSeq = __mlSequences[oImg._getexif()[ORIENTATION_TAG] - 1]

		# Transpose the image
		for i in lSeq:
			oImg = oImg.transpose(i)

		# Save the image using the same format as we got it in
		oImg.save(sNewImg, sFormat)

		# Get the raw bytes
		sRet = sNewImg.getvalue()

	# If there's no sequence, return the image as is
	except Exception as e:
		sRet = image

	# Cleanup
	oImg.close()
	sImg.close()
	sNewImg.close()

	# Return
	return sRet

def convertToJPEG(image):
	"""Convert To JPEG

	Changes any valid image into a JPEG

	Arguments:
		image {str} -- A raw image as a string

	Returns:
		str
	"""

	# Load the image into a new StringIO
	sImg = StringIO(image)

	# Create an empty StringIO for the new image
	sNewImg = StringIO('')

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# If the mode is not valid
	if oImg.mode not in ('1','L','RGB','RGBA'):
		oImg = oImg.convert('RGB');

	# Save the new image as a JPEG
	oImg.save(sNewImg, 'JPEG')

	# Pull out the raw string
	sRet = sNewImg.getvalue()

	# Close the image
	oImg.close()

	# Return the new image
	return sRet

def info(image):
	"""Info

	Returns information about an image: resolution, length, type, and mime

	Arguments:
		image {str} -- A raw image as a string

	Returns:
		dict
	"""

	# Load the image into a new StringIO
	sImg = StringIO(image)

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# Get the details
	dInfo = {
		"length": len(image),
		"mime": oImg.format in Pillow.MIME and Pillow.MIME[oImg.format] or None,
		"resolution": oImg.size,
		"type": oImg.format
	}

	# Check for exif rotation data
	try:
		dRet['orientation'] = oImg._getexif()[ORIENTATION_TAG]
	except Exception:
		dRet['orientation'] = False

	# Cleanup
	sImg.close()
	oImg.close()

	# Return the info
	return dInfo

def resize(image, dims, crop=False):
	"""Resize

	Given raw data and a size, a new image is created and returned as raw data

	Arguments:
		image {str} -- Raw image data to be loaded and resized
		dims {str|dict} -- New dimensions of the image, "WWWxHHH" or {"w":, "h":}
		crop {bool} -- Set to true to crop the photo rather than add whitespace

	Returns:
		str
	"""

	# Check the dimensions
	if not isinstance(dims, dict):
		if isinstance(dims, str):
			l = [i for i in size.split('x')]
			dims = {"w": l[0], "h": l[1]}
		else:
			raise ValueError('dims')

	# Load the image into a new StringIO
	sImg = StringIO(image)
	sNewImg = StringIO('')

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# Make sure the values are ints
	dims['w'] = int(dims['w'])
	dims['h'] = int(dims['h'])

	# Create a new blank image
	oNewImg = Pillow.new(oImg.mode, [dims['w'],dims['h']], (255,255,255,255))

	# If we are cropping
	if crop:
		dResize = Resize.crop(oImg.width, oImg.height, dims['w'], dims['h'])

	# Else, we are fitting
	else:
		dResize = Resize.fit(oImg.width, oImg.height, dims['w'], dims['h'])

	# Resize the image
	oImg.thumbnail([dResize['w'], dResize['h']], Pillow.ANTIALIAS)

	# Get the offsets
	lOffset = ((dims['w'] - dResize['w']) / 2, (dims['h'] - dResize['h']) / 2)

	# Paste the resized image onto the new canvas
	oNewImg.paste(oImg, lOffset)

	# Save the new image to a StringIO
	oNewImg.save(sNewImg, oImg.format)

	# Pull out the raw string
	sReturn = sNewImg.getvalue()

	# Cleanup
	oNewImg.close()
	oImg.close()
	sImg.close()

	# Return the new string
	return sReturn
