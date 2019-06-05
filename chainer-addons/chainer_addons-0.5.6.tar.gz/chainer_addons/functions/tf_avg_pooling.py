import chainer
from chainer.functions.pooling.average_pooling_2d import AveragePooling2D
from chainer import cuda


class TFAveragePooling2D(AveragePooling2D):
	"""
		The only thing, that changes is the CuDNN poolgin option from
			CUDNN_POOLING_AVERAGE_COUNT_INCLUDE_PADDING
		to
			CUDNN_POOLING_AVERAGE_COUNT_EXCLUDE_PADDING

		Note: CuDNN is required for this Function
	"""

	def __init__(self, *args, **kwargs):
		super(TFAveragePooling2D, self).__init__(*args, **kwargs)


	def create_pool_desc(self):
		assert chainer.should_use_cudnn('>=auto'), \
			"This function works only with CuDNN!"
		return cuda.cudnn.create_pooling_descriptor(
			(self.kh, self.kw), (self.sy, self.sx), (self.ph, self.pw),
			cuda.cuda.cudnn.CUDNN_POOLING_AVERAGE_COUNT_EXCLUDE_PADDING)


def tf_average_pooling_2d(x, ksize, stride=None, pad=0):
	return TFAveragePooling2D(ksize, stride, pad, cover_all=False).apply((x,))[0]
