import keras.backend as K
import tensorflow as tf


class Metrics(object):

	@staticmethod
	def absolute_relative_error(y, y_pred):
		error = K.sum(K.abs(y - y_pred))
		return error/K.sum(y)

	@staticmethod
	def model_accuracy(y, y_pred):
		with tf.Session().as_default():
			return 1 - Metrics.absolute_relative_error(y, y_pred).eval()

