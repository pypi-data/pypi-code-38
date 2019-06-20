import numpy as np
import abc
import warnings
import logging
from os.path import join, isfile, isdir
from collections import defaultdict, OrderedDict

from cvdatasets.utils import read_info_file, feature_file_name
from cvdatasets.dataset import Dataset

# def _parse_index(idx, offset):
# 	if idx.isdigit():
# 		idx = str(int(idx) - offset)
# 	return idx

class BBoxMixin(abc.ABC):
	def _load_bounding_boxes(self):
		assert self._bounding_boxes is not None, "Bouding boxes were not loaded!"

		uuid_to_bbox = {}
		for content in [i.split() for i in self._bounding_boxes]:
			uuid, bbox = content[0], content[1:]
			uuid_to_bbox[uuid] = [float(i) for i in bbox]

		self.bounding_boxes = np.array(
			[tuple(uuid_to_bbox[uuid]) for uuid in self.uuids],
			dtype=self.meta.bounding_box_dtype)

	def bounding_box(self, uuid):
		return self.bounding_boxes[self.uuid_to_idx[uuid]].copy()


class BaseAnnotations(abc.ABC):

	FEATURE_PHONY = dict(train=["train"], test=["test", "val"])

	def __init__(self, root_or_infofile, parts=None, feature_model=None):
		super(BaseAnnotations, self).__init__()
		self.part_type = parts
		self.feature_model = feature_model

		if isdir(root_or_infofile):
			self.info = None
			self.root = root_or_infofile
		elif isfile(root_or_infofile):
			self.root = self.root_from_infofile(root_or_infofile, parts)
		else:
			raise ValueError("Root folder or info file does not exist: \"{}\"".format(
				root_or_infofile
			))

		for fname, attr in self.meta.structure:
			self.read_content(fname, attr)

		self._load_uuids()
		self._load_labels()
		self._load_parts()
		self._load_split()

	@property
	def data_root(self):
		if self.info is None: return None
		return join(self.info.BASE_DIR, self.info.DATA_DIR)

	@property
	def dataset_info(self):
		if self.info is None: return None
		if self.part_type is None:
			return self.info.DATASETS[self.__class__.name]
		else:
			return self.info.PARTS[self.part_type]

	def root_from_infofile(self, info_file, parts=None):
		self.info = read_info_file(info_file)

		dataset_info = self.dataset_info
		annot_dir = join(self.data_root, dataset_info.folder, dataset_info.annotations)

		assert isdir(annot_dir), "Annotation folder does exist! \"{}\"".format(annot_dir)
		return annot_dir

	def new_dataset(self, subset=None, dataset_cls=Dataset, **kwargs):
		if subset is not None:
			uuids = getattr(self, "{}_uuids".format(subset))
		else:
			uuids = self.uuids

		kwargs = self.check_parts_and_features(subset, **kwargs)
		return dataset_cls(uuids=uuids, annotations=self, **kwargs)

	def check_parts_and_features(self, subset, **kwargs):
		dataset_info = self.dataset_info
		if dataset_info is None:
			return kwargs
		logging.debug("Dataset info: {}".format(dataset_info))

		# TODO: pass all scales
		new_opts = {}

		if "scales" in dataset_info:
			new_opts["ratio"] = dataset_info.scales[0]

		if "is_uniform" in dataset_info:
			new_opts["uniform_parts"] = dataset_info.is_uniform

		if self.part_type is not None:
			new_opts["part_rescale_size"] = dataset_info.rescale_size

		if None not in [subset, self.feature_model]:
			tried = []
			model_info = self.info.MODELS[self.feature_model]
			for subset_phony in BaseAnnotations.FEATURE_PHONY[subset]:
				features = feature_file_name(subset_phony, dataset_info, model_info)
				feature_path = join(self.root, "features", features)
				if isfile(feature_path): break
				tried.append(feature_path)
			else:
				raise ValueError(
					"Could not find any features in \"{}\" for {} subset. Tried features: {}".format(
					join(self.root, "features"), subset, tried))

			logging.info("Using features file from \"{}\"".format(feature_path))
			new_opts["features"] = feature_path
		new_opts.update(kwargs)

		logging.debug("Final kwargs: {}".format(new_opts))
		return new_opts

	@property
	def has_parts(self):
		return hasattr(self, "_part_locs") and self._part_locs is not None

	@property
	@abc.abstractmethod
	def meta(self):
		pass

	def _path(self, file):
		return join(self.root, file)

	def _open(self, file):
		return open(self._path(file))

	def read_content(self, file, attr):
		content = None
		fpath = self._path(file)
		if isfile(fpath):
			with self._open(file) as f:
				content = [line.strip() for line in f if line.strip()]
		else:
			warnings.warn("File \"{}\" was not found!".format(fpath))

		setattr(self, attr, content)


	def _load_labels(self):
		self.labels = np.array([int(l) for l in self.labels], dtype=np.int32)

	def _load_uuids(self):
		assert self._images is not None, "Images were not loaded!"
		uuid_fnames = [i.split() for i in self._images]
		self.uuids, self.images = map(np.array, zip(*uuid_fnames))
		self.uuid_to_idx = {uuid: i for i, uuid in enumerate(self.uuids)}

	def _load_parts(self):
		assert self.has_parts, "Part locations were not loaded!"
		# this part is quite slow... TODO: some runtime improvements?
		uuid_to_parts = defaultdict(list)
		for content in [i.split() for i in self._part_locs]:
			uuid = content[0]
			# assert uuid in self.uuids, \
			# 	"Could not find UUID \"\" from part annotations in image annotations!".format(uuid)
			uuid_to_parts[uuid].append([float(c) for c in content[1:]])

		uuid_to_parts = dict(uuid_to_parts)
		self.part_locs = np.stack([
			uuid_to_parts[uuid] for uuid in self.uuids]).astype(int)

		if hasattr(self, "_part_names") and self._part_names is not None:
			self._load_part_names()

	def _load_part_names(self):
		self.part_names = OrderedDict()
		self.part_name_list = []
		for line in self._part_names:
			part_idx, _, name = line.partition(" ")
			self.part_names[int(part_idx)] = name
			self.part_name_list.append(name)

	def _load_split(self):
		assert self._split is not None, "Train-test split was not loaded!"
		uuid_to_split = {uuid: int(split) for uuid, split in zip(self.uuids, self._split)}
		self.train_split = np.array([uuid_to_split[uuid] for uuid in self.uuids], dtype=bool)
		self.test_split = np.logical_not(self.train_split)

	def image_path(self, image):
		return join(self.root, self.meta.images_folder, image)

	def image(self, uuid):
		fname = self.images[self.uuid_to_idx[uuid]]
		return self.image_path(fname)

	def label(self, uuid):
		return self.labels[self.uuid_to_idx[uuid]].copy()

	def parts(self, uuid):
		return self.part_locs[self.uuid_to_idx[uuid]].copy()


	def _uuids(self, split):
		return self.uuids[split]

	@property
	def train_uuids(self):
		return self._uuids(self.train_split)

	@property
	def test_uuids(self):
		return self._uuids(self.test_split)

