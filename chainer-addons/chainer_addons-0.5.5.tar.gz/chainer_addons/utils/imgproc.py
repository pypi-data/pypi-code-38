import numpy as np
from functools import reduce, partial, wraps
from chainercv.transforms import center_crop, resize, scale

def asarray(func):

	@wraps(func)
	def inner(image, *args, **kw):
		from PIL import Image
		from scipy.misc import fromimage, toimage
		is_pil = isinstance(image, Image.Image)
		if is_pil:
			image = fromimage(image)
		image = func(image, *args, **kw)
		if is_pil:
			image = toimage(image)
		return image

	return inner

def crop(image, x,y,w,h):
	return image[:, y: y + h, x: x + w]

@asarray
def random_horizontal_flip(image, threshold=.5, axis=2):
	if np.random.random() < threshold:
		return np.flip(image, axis=axis)
	return image

@asarray
def random_crop(image, crop_size):
	th, tw = crop_size
	c, h, w = image.shape
	th, tw = min(th, h), min(tw, w)
	x = np.random.randint(0, w - tw)
	y = np.random.randint(0, h - th)
	return crop(image, x, y, th, tw)

@asarray
def _center_crop(image, crop_size):
	th, tw = crop_size
	c, h, w = image.shape
	th, tw = min(th, h), min(tw, w)
	x = int((w - tw) / 2.)
	y = int((h - th) / 2.)
	return crop(image, x, y, th, tw)


def generic_prepare(im, size,
		crop_fraction=0.875,
		swap_channels=True,
		zero_mean=False,
		keep_ratio=True
	):

	crop_size = None
	h, w, c = im.shape


	_im = im.transpose(2, 0, 1)

	if swap_channels:
		# RGB -> BGR
		_im = _im[::-1]

	if crop_fraction:
		crop_size = (np.array([h, w]) * crop_fraction).astype(np.int32)
		_im = center_crop(_im, crop_size)

	# bilinear interpolation
	if keep_ratio:
		if isinstance(size, tuple):
			size = size[0]
		_im = scale(_im, size, interpolation=2)
	else:
		if isinstance(size, int):
			size = (size, size)
		_im = resize(_im, size, interpolation=2)

	if _im.dtype == np.uint8:
		# rescale [0 .. 255] -> [0 .. 1]
		_im = (_im / 255).astype(np.float32)


	if zero_mean:
		# rescale [0 .. 1] -> [-1 .. 1]
		_im = _im * 2 - 1

	return _im


def generic_tf_prepare(size, crop_fraction=0.875, from_path=False):

	import tensorflow as tf
	config_sess = tf.ConfigProto(allow_soft_placement=True)
	config_sess.gpu_options.allow_growth = True
	sess = tf.Session(config=config_sess)

	if from_path:
		im_input = tf.placeholder(tf.string)
		image = tf.image.decode_jpeg(tf.read_file(im_input), channels=3)
		image = tf.image.convert_image_dtype(image, tf.float32)
	else:
		image = im_input = tf.placeholder(tf.float32, shape=(None, None, 3))


	raise NotImplementedError("REFACTOR ME!")
	image = tf.image.central_crop(image, central_fraction=crop_fraction)
	image = tf.expand_dims(image, 0)
	image = tf.image.resize_bilinear(image, [size, size], align_corners=False)
	image = tf.squeeze(image, [0])
	image = tf.subtract(image, 0.5)
	output = tf.multiply(image, 2)

	def inner(im):
		if not from_path and im.dtype == np.uint8:
			im = im / 255

		res = sess.run(output, feed_dict={im_input: im})
		return res.transpose(2, 0, 1)

	return inner


class Augmentation(object):
	def __init__(self):
		self.augmentations = []

	def __call__(self, image):
		if not self.augmentations: return image
		def call(val, func):
			return func(val)
		return reduce(
			call, self.augmentations,
			image)

	def center_crop(self, size):
		self.augmentations.append(
			partial(_center_crop, crop_size=size))
		return self

	def random_crop(self, size):
		self.augmentations.append(
			partial(random_crop, crop_size=size))
		return self

	def random_horizontal_flip(self, threshold=.5, axis=2):

		self.augmentations.append(
			partial(random_horizontal_flip, threshold=threshold, axis=axis))
		return self
