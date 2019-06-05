import chainer
import chainer.links as L
import chainer.functions as F

import numpy as np
import six
from os.path import isfile
from chainercv.transforms import resize, scale

from .base import PretrainedModelMixin

from functools import partial


class AlexNet(PretrainedModelMixin, chainer.Chain):

	class meta:
		classifier_layers = ["fc6", "fc7", "fc8"]
		conv_map_layer = "pool5"
		feature_layer = "fc7"
		feature_size = 4096
		n_conv_maps = 256
		input_size = 227

		mean = None

		@classmethod
		def get_mean(cls, f='/tmp/ilsvrc_2012_mean.npy'):
			if not isfile(f) and cls.mean is None:
				print('Downloading ILSVRC12 mean file for NumPy...')
				six.moves.urllib.request.urlretrieve(
					'https://github.com/BVLC/caffe/raw/master/python/caffe/imagenet/ilsvrc_2012_mean.npy', f)
				print('Done')

			print('Loading ILSVRC12 mean file from \"{}\"'.format(f))
			cls.mean = np.load(f).astype(np.float32)
			c,h,w = cls.mean.shape

			dh, dw = int((h - cls.input_size) / 2), int((w - cls.input_size) // 2)
			cls.mean = cls.mean[:, dh:dh + cls.input_size, dw:dw + cls.input_size]

		@staticmethod
		def prepare_func(x, size=None, swap_channels=True, keep_ratio=True):

			if size is None:
				size = AlexNet.meta.input_size
			elif isinstance(size, tuple):
				size = size[0]

			# HWC -> CHW channel order
			x = x.astype(np.float32).transpose(2,0,1)


			if keep_ratio:
				# scale the smallest side to <size>
				x = scale(x, size=size)
			else:
				# resize the image to  side to <size>x<size>
				x = resize(x, (size, size))

			if swap_channels:
				x = x[::-1]

			return x - AlexNet.meta.mean

	@classmethod
	def prepare_back(cls, img):
		img = (img + cls.meta.mean).transpose(1,2,0)
		img = img[..., ::-1].astype(np.uint8)
		return img

	@property
	def _links(self):

		links = [
			("conv1", [
				self.conv1, F.relu,
				partial(F.max_pooling_2d, ksize=3, stride=2),
				F.local_response_normalization]
			),
			("conv2", [
				self.conv2, F.relu,
				partial(F.max_pooling_2d, ksize=3, stride=2),
				F.local_response_normalization]
			),
			("conv3", [self.conv3, F.relu]),
			("conv4", [self.conv4, F.relu]),
			("conv5", [self.conv5, F.relu]),
			("pool5", [partial(F.max_pooling_2d, ksize=3, stride=2)]),
			('fc6', [self.fc6, F.relu]),
			('fc7', [self.fc7, F.relu]),
			('fc8', [self.fc8]),
			('prob', [F.softmax]),
		]

		return links



	def init_layers(self, n_classes, **kwargs):
		AlexNet.meta.get_mean()

		self.conv1 = L.Convolution2D(  3,  96, 11, stride=4, pad=0)
		self.conv2 = L.Convolution2D( 96, 256,  5, stride=1, pad=2)
		self.conv3 = L.Convolution2D(256, 384,  3, stride=1, pad=1)
		self.conv4 = L.Convolution2D(384, 384,  3, stride=1, pad=1)
		self.conv5 = L.Convolution2D(384, 256,  3, stride=1, pad=1)

		self.fc6 = L.Linear(13*13*256, 4096)
		self.fc7 = L.Linear(4096, 4096)
		self.fc8 = L.Linear(4096, n_classes)


	def __call__(self, x, layer_name='fc'):
		for key, funcs in self.functions.items():
			for func in funcs:
				x = func(x)
			if key == layer_name:
				return x
