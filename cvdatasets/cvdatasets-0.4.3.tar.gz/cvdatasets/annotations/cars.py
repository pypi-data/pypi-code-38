import numpy as np

from os.path import join

from cvdatasets.utils import _MetaInfo
from .base import BaseAnnotations, BBoxMixin


class CARS_Annotations(BaseAnnotations, BBoxMixin):
	name="CARS"

	@property
	def meta(self):
		info = _MetaInfo(
			images_folder="images",
			images_file="images.txt",
			labels_file="labels.txt",
			split_file="tr_ID.txt",
			bounding_boxes="bounding_boxes.txt",
			bounding_box_dtype=np.dtype([(v, np.int32) for v in "xywh"]),
			parts_file=join("parts", "part_locs.txt"),
			part_names_file=join("parts", "parts.txt"),
		)

		info.structure = [
			[info.images_file, "_images"],
			[info.labels_file, "labels"],
			[info.split_file, "_split"],
			[info.parts_file, "_part_locs"],
			[info.part_names_file, "_part_names"],
			[info.bounding_boxes, "_bounding_boxes"],
		]
		return info

	def __init__(self, *args, **kwargs):
		super(CARS_Annotations, self).__init__(*args, **kwargs)
		# set labels from [1..N] to [0..N-1]
		self.labels -= 1

	def _load_parts(self):
		self.part_names = {}

		# load only if present
		if self.has_parts:
			super(CARS_Annotations, self)._load_parts()

		self._load_bounding_boxes()

	def parts(self, *args, **kwargs):
		if self.has_parts:
			return super(CARS_Annotations, self).parts(*args, **kwargs)
		return None
