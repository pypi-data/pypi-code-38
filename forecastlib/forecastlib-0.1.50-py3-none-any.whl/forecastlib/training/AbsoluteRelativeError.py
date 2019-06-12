import keras.backend as K


class AbsoluteRelativeError(object):

	@staticmethod
	def get(y, y_pred):
		error = K.sum(K.abs(y - y_pred))
		return error/K.sum(y)
