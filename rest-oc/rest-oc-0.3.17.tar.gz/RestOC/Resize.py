# coding=utf8
"""Resize

Common functions for resizing dimensions to fit, to crop, etc
"""

__author__ = "Chris Nasr"
__copyright__ = "FUEL for the FIRE"
__version__ = "1.0.0"
__created__ = "2018-11-11"

def crop(w, h, bw, bh):
	"""Crop

	Makes sure one side fits and crops the other

	Arguments:
		w {int} -- The current width
		h {int} -- The current height
		bw {int} -- The boundary width
		bh {int} -- The boundary height

	Returns:
		dict
	"""

	# Init the return
	dRet = {}

	# Easier to work with floats
	w = float(w)
	h = float(h)

	# If the image is already smaller, make it bigger
	if w < bw or h < bh:

		# Which is the side that needs to grow more?
		if (bw / w) > (bh / h):
			dRet['w'] = bw
			dRet['h'] = int(round(bw * (h / w)))
		else:
			dRet['w'] = int(round(bh * (w / h)))
			dRet['h'] = bh

	# Else, make it smaller
	else:

		# Which is the side that needs to shrink less?
		if (w / bw) > (h / bh):
			dRet['w'] = int(round(bh * (w / h)))
			dRet['h'] = bh
		else:
			dRet['w'] = bw
			dRet['h'] = int(round(bw * (h / w)))

	# Return the new width and height
	return dRet

def fit(w, h, bw, bh):
	"""Fit

	Makes sure one side fits and makes the other smaller than necessary

	Arguments:
		w {int} -- The current width
		h {int} -- The current height
		bw {int} -- The boundary width
		bh {int} -- The boundary height

	Returns:
		list [w, h]
	"""

	# Init the return
	dRet = {}

	# Easier to work with floats
	w = float(w)
	h = float(h)

	# If the image is already smaller, make it bigger
	if w < bw and h < bh:

		# Figure out the larger side
		if (bw / w) > (bh / h):
			dRet['w'] = int(round(bh * (w / h)))
			dRet['h'] = bh
		else:
			dRet['w'] = bw
			dRet['h'] = int(round(bw * (h / w)))

	# Else, make it smaller
	else:

		# Figure out the larger side
		if (w / bw) > (h / bh):
			dRet['w'] = bw
			dRet['h'] = int(round(bw * (h / w)))
		else:
			dRet['w'] = int(round(bh * (w / h)))
			dRet['h'] = bh

	# Return the new width and height
	return dRet

def region(w, h, bw, bh):
	"""Region

	Returns a new set of region points based on a current width and height and
	the bounding box

	Arguments:
		w {int} -- The current width
		h {int} -- The current height
		bw {int} -- The boundary width
		bh {int} -- The boundary height

	Returns:
		dict
	"""

	# Return
	dRet = {}

	# If the current width is larger than the bounds width
	if w > bw:

		dRet['x'] = int(round((w - bw) / 2.0))
		dRet['y'] = 0
		dRet['w'] = int(bw + round((w - bw) / 2.0))
		dRet['h'] = bh

	# Else if the current height is larger than the bounds height
	else:

		dRet['x'] = 0
		dRet['y'] = int(round((h - bh) / 2.0))
		dRet['w'] = bw
		dRet['h'] = int(bh + round((h - bh) / 2.0))

	# Return the region
	return dRet
