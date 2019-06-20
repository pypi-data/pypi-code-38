import numpy as np

from os.path import isfile

from . import BaseMixin


class PreExtractedFeaturesMixin(BaseMixin):

	def __size_check(self):
		assert len(self.features) == len(self), \
			"Number of features ({}) does not match the number of images ({})!".format(
				len(self.features), len(self)
			)

	def __init__(self, features=None, *args, **kw):
		super(PreExtractedFeaturesMixin, self).__init__(*args, **kw)

		self.features = None
		if features is not None and isfile(features):
			self.features = self.load_features(features)
			self.__size_check()

	def load_features(self, features_file):
		"""
			Default feature loading from a file.
			If you desire another feature loading logic,
			subclass this mixin and override this method.
		"""
		try:
			cont = np.load(features_file)
			return cont["features"]
		except Exception as e:
			msg = "Error occured while reading features: \"{}\". ".format(e) + \
				"If you want another feature loading logic, override this method!"
			raise ValueError(msg)

	def get_example(self, i):
		im_obj = super(PreExtractedFeaturesMixin, self).get_example(i)
		if self.features is not None:
			im_obj.feature = self.features[i]

		return im_obj
