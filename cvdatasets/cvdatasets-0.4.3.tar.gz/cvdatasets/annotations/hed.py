import numpy as np
import simplejson as json

from os.path import join

from cvdatasets.utils import _MetaInfo

from .base import BaseAnnotations, BBoxMixin

class HED_Annotations(BaseAnnotations, BBoxMixin):

	name="HED"

	@property
	def meta(self):
		info = _MetaInfo(
			images_folder="images",

			images_file="images.txt",
			labels_file="labels.txt",
			split_file="tr_ID.txt",
			# fake bounding boxes: the whole image
			bounding_box_dtype=np.dtype([(v, np.int32) for v in "xywh"]),

			parts_file=join("parts", "part_locs.txt"),
			part_names_file=join("parts", "parts.txt"),
		)

		info.structure = [
			[info.images_file, "_images"],
			[info.labels_file, "labels"],
			[info.split_file, "_split"],
		]
		return info

	def parts(self, *args, **kwargs):
		if self.has_parts:
			return super(HED_Annotations, self).parts(*args, **kwargs)
		return None

	def _load_bounding_boxes(self):
		self.bounding_boxes = np.zeros(len(self.uuids),
			dtype=self.meta.bounding_box_dtype)

		for i in range(len(self.uuids)):
			self.bounding_boxes[i]["w"] = 224
			self.bounding_boxes[i]["h"] = 224

	def _load_parts(self):
		self.part_names = {}

		# load only if present
		if self.has_parts:
			super(HED_Annotations, self)._load_parts()

		self._load_bounding_boxes()
