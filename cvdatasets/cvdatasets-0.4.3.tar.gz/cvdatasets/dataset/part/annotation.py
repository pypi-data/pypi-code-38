import numpy as np

from matplotlib.patches import Rectangle
from functools import partial

from cvdatasets import utils
from .base import BasePart

class LocationPart(BasePart):
	DEFAULT_RATIO = np.sqrt(49 / 400) # 0.35

	def __init__(self, image, annotation, rescale_size=None):
		super(LocationPart, self).__init__()

		annotation = self.rescale(image, annotation, rescale_size)
		# here x,y are the center of the part
		self._id, self.x, self.y, self.is_visible = annotation
		self._ratio = LocationPart.DEFAULT_RATIO

	@property
	def as_annotation(self):
		return np.array([self._id, self.x, self.y, self.is_visible])

	def _generic_op(self, image, ratio, op):
		ratio = ratio or self._ratio
		_h, _w, _ = utils.dimensions(image)
		w, h = int(_w * ratio), int(_h * ratio)
		x, y = self.xy

		return op(image, x, y, w, h)

	def crop(self, image, ratio=None, padding_mode="edge", *args, **kwargs):

		def op(im, x, y, w, h):
			return super(LocationPart, self).crop(im, w, h,
				padding_mode, is_location=True)

		return self._generic_op(image, ratio, op)

	def reveal(self, im, ratio=None, *args, **kwargs):

		def op(im, x, y, w, h):
			x, y = max(x - w // 2, 0), max(y - h // 2, 0)
			return x, y, im[y:y+h, x:x+w]

		return self._generic_op(im, ratio, op)

	def plot(self, im, ax, ratio=None, fill=False, linestyle="--", **kwargs):
		if not self.is_visible: return

		def op(im, x, y, w, h):
			ax.add_patch(Rectangle(
				(x-w//2, y-h//2), w, h,
				fill=fill, linestyle=linestyle,
				**kwargs))

			ax.scatter(*self.middle, marker="x", color="white", alpha=0.8)
		return self._generic_op(im, ratio, op)


	@property
	def middle(self):
		return np.array([self.x, self.y])

class BBoxPart(BasePart):

	def __init__(self, image, annotation, rescale_size=None, center_cropped=True):
		super(BBoxPart, self).__init__()

		annotation = self.rescale(image, annotation, rescale_size, center_cropped)
		# here x,y are top left corner of the part
		self._id, self.x, self.y, self.w, self.h = annotation
		self.is_visible = True

	@property
	def as_annotation(self):
		return np.array([self._id, self.x, self.y, self.w, self.h])

	def rescale(self, image, annotation, rescale_size, center_cropped=True):

		if rescale_size is not None and rescale_size > 0:
			from chainer_addons.utils.imgproc import _center_crop

			annotation = super(BBoxPart, self).rescale(image, annotation, rescale_size, center_cropped)

			# base class rescales only x and y.
			# now we need to rescale the width and height.

			wh = annotation[3:5]
			new_wh = utils.rescale(image, wh, rescale_size, center_cropped, no_offset=True)
			annotation[3:5] = new_wh

		return annotation

	@property
	def middle(self):
		return np.array([self.x + self.w // 2, self.y + self.h // 2])

	def crop(self, image, padding_mode="edge", *args, **kwargs):
		return super(BBoxPart, self).crop(image, self.w, self.h,
			padding_mode, is_location=False)

	def reveal(self, im, ratio, *args, **kwargs):
		_h, _w, c = utils.dimensions(im)
		x,y = self.xy
		return x, y, im[y:y+self.h, x:x+self.w]



	def plot(self, im, ax, ratio, fill=False, linestyle="--", **kwargs):
		ax.add_patch(Rectangle(
			(self.x, self.y), self.w, self.h,
			fill=fill, linestyle=linestyle,
			**kwargs
		))

		ax.scatter(*self.middle, marker="x", color="white", alpha=0.8)

