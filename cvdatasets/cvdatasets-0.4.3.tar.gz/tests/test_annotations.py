import unittest
import numpy as np
import os
import uuid

from tests.configs import config
from os.path import *

from abc import ABC, abstractproperty


from cvdatasets import BaseAnnotations, _MetaInfo
from cvdatasets.utils import read_info_file

class MockAnnotation(BaseAnnotations):
	name = "MOCK"
	index_offset = 0

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

class BaseAnnotationTest(unittest.TestCase, ABC):

	def tearDown(self):
		# clear mock data folder?
		pass

	def setUp(self):
		self.info = read_info_file(config.INFO_FILE)

	def create_annotations(self, images, labels, split,
		bboxes=False,
		index_offset=0,
		n_parts=None,
		annot_params={}):

		data_root = join(self.info.BASE_DIR, self.info.DATA_DIR)
		dataset_info = self.info.DATASETS.MOCK
		annot_dir = join(data_root, dataset_info.folder, dataset_info.annotations)

		if not isdir(annot_dir):
			os.makedirs(annot_dir)

		fname = lambda name: join(annot_dir, name)

		with open(fname("images.txt"), "w") as images_f,\
			open(fname("labels.txt"), "w") as labels_f,\
			open(fname("tr_ID.txt"), "w") as split_f:

			for im, lab, sp in zip(images, labels, split):
				print(*im, file=images_f)
				print(lab, file=labels_f)
				print(sp, file=split_f)

		if bboxes:
			with open(fname("bounding_boxes.txt"), "w") as bbox_f:
				for i in range(index_offset, index_offset + len(images)):
					print(i, 0, 0, 100, 100, file=bbox_f)

		if n_parts is not None:
			parts_dir = join(annot_dir, "parts")
			if not isdir(parts_dir):
				os.makedirs(parts_dir)
			fname = lambda name: join(parts_dir, name)
			with open(fname("parts.txt"), "w") as part_names_f, \
				open(fname("part_locs.txt"), "w") as part_locs_f:

				for i in range(n_parts):
					print(i, "part_{}".format(i), file=part_names_f)

				for i, imname in images:
					for p in range(n_parts):
						print(i, p, 10*(p+1), 10*(p+1), 1, file=part_locs_f)


		return MockAnnotation(
			root_or_infofile=config.INFO_FILE,
			**annot_params)


class AnnotationTest(BaseAnnotationTest):

	# @unittest.skip
	def test_simple(self):
		_annotation_params = dict(
			images=[(i, "images{}.jpg".format(i)) for i in range(10)],
			labels=[i % 5 for i in range(10)],
			split=[int(i < 5) for i in range(10)],
			bboxes=True,
			n_parts=5
		)
		annot = self.create_annotations(**_annotation_params)

	# @unittest.skip
	def test_with_uuids(self):
		_annotation_params = dict(
			images=[(uuid.uuid4(), "images{}.jpg".format(i)) for i in range(10)],
			labels=[i % 5 for i in range(10)],
			split=[int(i < 5) for i in range(10)],
			bboxes=True,
			n_parts=5
		)
		annot = self.create_annotations(**_annotation_params)

		self.assertFalse(0)
