import numpy as np

from cvdatasets import utils

from .base import BasePartCollection, BasePart
from .annotation import BBoxPart

class Parts(BasePartCollection):

	def __init__(self, image, part_annotations, *args, **kwargs):
		super(Parts, self).__init__()
		if part_annotations is None:
			self._parts = []
		else:
			self._parts = [BasePart.new(image, a, *args, **kwargs) for a in part_annotations]


class UniformParts(BasePartCollection):

	def __init__(self, image, ratio):
		super(UniformParts, self).__init__()
		self._parts = list(self.generate_parts(image, ratio))

	def generate_parts(self, im, ratio, round_op=np.floor):
		h, w, c = utils.dimensions(im)

		part_w = round_op(w * ratio).astype(np.int32)
		part_h = round_op(h * ratio).astype(np.int32)

		n, m = w // part_w, h // part_h

		# fit best possible part_w and part_h
		part_w = int(w / n)
		part_h = int(h / m)

		for i in range(n*m):
			row, col = np.unravel_index(i, (n, m))
			x, y = col * part_w, row * part_h

			yield BBoxPart(im, [i, x, y, part_w, part_h], center_cropped=False)
