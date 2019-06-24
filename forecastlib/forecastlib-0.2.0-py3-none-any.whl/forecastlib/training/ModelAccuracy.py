import tensorflow as tf

from . import AbsoluteRelativeError


class ModelAccuracy(object):
	def get(y, y_pred):
		with tf.Session().as_default():
			return 1 - AbsoluteRelativeError.get(y, y_pred).eval()
