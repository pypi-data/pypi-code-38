import numpy as np

from os.path import join

from cvdatasets.utils import _MetaInfo
from .base import BaseAnnotations


class NAB_Annotations(BaseAnnotations):
	name="NABirds"

	@property
	def meta(self):
		info = _MetaInfo(
			images_folder="images",
			images_file="images.txt",
			labels_file="labels.txt",
			hierarchy_file="hierarchy.txt",
			split_file="train_test_split.txt",
			bounding_box_dtype=np.dtype([(v, np.int32) for v in "xywh"]),
			parts_file=join("parts", "part_locs.txt"),
			part_names_file=join("parts", "parts.txt"),
		)

		info.structure = [
			[info.images_file, "_images"],
			[info.labels_file, "labels"],
			[info.hierarchy_file, "hierarchy"],
			[info.split_file, "_split"],
			[info.parts_file, "_part_locs"],
			[info.part_names_file, "_part_names"],
		]
		return info

	def _load_split(self):
		assert self._split is not None, "Train-test split was not loaded!"
		uuid_to_split = {uuid: int(split) for uuid, split in [i.split() for i in self._split]}
		self.train_split = np.array([uuid_to_split[uuid] for uuid in self.uuids], dtype=bool)
		self.test_split = np.logical_not(self.train_split)

