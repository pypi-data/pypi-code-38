import numpy as np
from PIL.Image import Image as PIL_Image

def rescale(im, coords, rescale_size, center_cropped=True, no_offset=False):
	h, w, c = dimensions(im)

	offset = 0
	if center_cropped:
		_min_val = min(w, h)
		wh = np.array([_min_val, _min_val])
		if not no_offset:
			offset = (np.array([w, h]) - wh) / 2
	else:
		wh = np.array([w, h])

	scale = wh / rescale_size
	return coords * scale + offset

def dimensions(im):
	if isinstance(im, np.ndarray):
		if im.ndim != 3:
			import pdb; pdb.set_trace()
		assert im.ndim == 3, "Only RGB images are currently supported!"
		return im.shape
	elif isinstance(im, PIL_Image):
		w, h = im.size
		c = len(im.getbands())
		# assert c == 3, "Only RGB images are currently supported!"
		return h, w, c
	else:
		raise ValueError("Unknown image instance ({})!".format(type(im)))

def asarray(im, dtype=np.uint8):
	if isinstance(im, np.ndarray):
		return im.astype(dtype)
	elif isinstance(im, PIL_Image):
		return np.asarray(im, dtype=dtype)
	else:
		raise ValueError("Unknown image instance ({})!".format(type(im)))
