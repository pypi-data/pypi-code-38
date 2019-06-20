import numpy as np

from os.path import join

from . import BaseMixin
from ..image import ImageWrapper

class AnnotationsReadMixin(BaseMixin):

	def __init__(self, uuids, annotations, part_rescale_size=None, center_cropped=True, mode="RGB"):
		super(AnnotationsReadMixin, self).__init__()
		self.uuids = uuids
		self._annot = annotations
		self.mode = mode
		self.part_rescale_size = part_rescale_size
		self.center_cropped = center_cropped

	def __len__(self):
		return len(self.uuids)

	def _get(self, method, i):
		return getattr(self._annot, method)(self.uuids[i])

	def get_example(self, i):
		# res = super(AnnotationsReadMixin, self).get_example(i)
		# # if the super class returns something, then the class inheritance is wrong
		# assert res is None, "AnnotationsReadMixin should be the last class in the hierarchy!"

		methods = ["image", "parts", "label"]
		im_path, parts, label = [self._get(m, i) for m in methods]

		return ImageWrapper(im_path, int(label), parts,
			mode=self.mode,
			part_rescale_size=self.part_rescale_size,
			center_cropped=self.center_cropped)

	@property
	def n_parts(self):
		return self._annot.part_locs.shape[1]

	@property
	def labels(self):
		return np.array([self._get("label", i) for i in range(len(self))])


class ImageListReadingMixin(BaseMixin):

	def __init__(self, pairs, root="."):
		super(ImageListReadingMixin, self).__init__()
		with open(pairs) as f:
			self._pairs = [line.strip().split() for line in f]

		assert all([len(pair) == 2 for pair in self._pairs]), \
			"Invalid format of the pairs file!"

		self._root = root

	def __len__(self):
		return len(self._pairs)

	def get_example(self, i):
		im_file, label = self._pairs[i]
		im_path = join(self._root, im_file)

		return ImageWrapper(im_path, int(label))

	@property
	def labels(self):
		return np.array([label for (_, label) in self._pairs])

