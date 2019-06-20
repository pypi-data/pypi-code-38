import numpy as np

from os.path import join

from cvdatasets.utils import _MetaInfo
from .base import BaseAnnotations, BBoxMixin


class DOGS_Annotations(BaseAnnotations, BBoxMixin):
	name="DOGS"

	@property
	def meta(self):
		info = _MetaInfo(
			images_folder="images",
			images_file="images.txt",
			labels_file="labels.txt",
			split_file="tr_ID.txt",
			bounding_boxes="bounding_boxes.txt",
			bounding_box_dtype=np.dtype([(v, np.int32) for v in "xywh"]),
			# parts_file=join("parts", "part_locs.txt"),
			# part_names_file=join("parts", "parts.txt"),

		)

		info.structure = [
			[info.images_file, "_images"],
			[info.labels_file, "labels"],
			[info.split_file, "_split"],
			[info.bounding_boxes, "_bounding_boxes"],
			# [info.parts_file, "_part_locs"],
			# [info.part_names_file, "_part_names"],
		]
		return info


	def parts(self, *args, **kwargs):
		if self.has_parts:
			return super(DOGS_Annotations, self).parts(*args, **kwargs)
		return None

	def _load_parts(self):
		self.part_names = {}

		# load only if present
		if self.has_parts:
			super(DOGS_Annotations, self)._load_parts()

		self._load_bounding_boxes()
