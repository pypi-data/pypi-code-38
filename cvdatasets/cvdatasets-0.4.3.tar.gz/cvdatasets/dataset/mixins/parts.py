import numpy as np

from . import BaseMixin

class BBCropMixin(BaseMixin):

	def __init__(self, crop_to_bb=False, crop_uniform=False, *args, **kwargs):
		super(BBCropMixin, self).__init__(*args, **kwargs)
		self.crop_to_bb = crop_to_bb
		self.crop_uniform = crop_uniform

	def bounding_box(self, i):
		bbox = self._get("bounding_box", i)
		x,y,w,h = [bbox[attr] for attr in "xywh"]
		if self.crop_uniform:
			x0 = x + w//2
			y0 = y + h//2

			crop_size = max(w//2, h//2)

			x,y = max(x0 - crop_size, 0), max(y0 - crop_size, 0)
			w = h = crop_size * 2
		return x,y,w,h

	def get_example(self, i):
		im_obj = super(BBCropMixin, self).get_example(i)
		if self.crop_to_bb:
			bb = self.bounding_box(i)
			return im_obj.crop(*bb)
		return im_obj

class PartsInBBMixin(BaseMixin):
	def __init__(self, parts_in_bb=False, *args, **kwargs):
		super(PartsInBBMixin, self).__init__(*args, **kwargs)
		self.parts_in_bb = parts_in_bb

	def get_example(self, i):
		im_obj = super(PartsInBBMixin, self).get_example(i)

		if self.parts_in_bb:
			bb = self.bounding_box(i)
			return im_obj.hide_parts_outside_bb(*bb)
		return im_obj

class PartCropMixin(BaseMixin):

	def __init__(self, return_part_crops=False, *args, **kwargs):
		super(PartCropMixin, self).__init__(*args, **kwargs)
		self.return_part_crops = return_part_crops

	def get_example(self, i):
		im_obj = super(PartCropMixin, self).get_example(i)
		if self.return_part_crops:
			return im_obj.part_crops(self.ratio)
		return im_obj


class PartRevealMixin(BaseMixin):

	def __init__(self, reveal_visible=False, *args, **kwargs):
		super(PartRevealMixin, self).__init__(*args, **kwargs)
		self.reveal_visible = reveal_visible

	def get_example(self, i):
		im_obj = super(PartRevealMixin, self).get_example(i)
		assert hasattr(self, "ratio"), "\"ratio\" attribute is missing!"
		if self.reveal_visible:
			return im_obj.reveal_visible(self.ratio)
		return im_obj


class UniformPartMixin(BaseMixin):

	def __init__(self, uniform_parts=False, ratio=None, *args, **kwargs):
		super(UniformPartMixin, self).__init__(*args, **kwargs)
		self.uniform_parts = uniform_parts
		self.ratio = ratio

	def get_example(self, i):
		im_obj = super(UniformPartMixin, self).get_example(i)
		if self.uniform_parts:
			return im_obj.uniform_parts(self.ratio)
		return im_obj

class RandomBlackOutMixin(BaseMixin):

	def __init__(self, seed=None, rnd_select=False, blackout_parts=None, *args, **kwargs):
		super(RandomBlackOutMixin, self).__init__(*args, **kwargs)
		self.rnd = np.random.RandomState(seed)
		self.rnd_select = rnd_select
		self.blackout_parts = blackout_parts

	def get_example(self, i):
		im_obj = super(RandomBlackOutMixin, self).get_example(i)
		if self.rnd_select:
			return im_obj.select_random_parts(rnd=self.rnd, n_parts=self.blackout_parts)
		return im_obj


# some shortcuts

class PartMixin(RandomBlackOutMixin, PartsInBBMixin, UniformPartMixin, BBCropMixin):
	"""
		TODO!
	"""

class RevealedPartMixin(PartRevealMixin, PartMixin):
	"""
		TODO!
	"""


class CroppedPartMixin(PartCropMixin, PartMixin):
	"""
		TODO!
	"""
