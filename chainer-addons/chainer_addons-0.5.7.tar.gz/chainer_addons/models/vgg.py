import numpy as np
import chainer.links as L
import chainer.functions as F

from chainer.links.model.vision.vgg import prepare

from .base import PretrainedModelMixin

from collections import OrderedDict

class VGG19Layers(PretrainedModelMixin, L.VGG16Layers):
	"""
		adds some additional layers to the original VGG16
		model definition. the last linear layer is also replaced
		if number of classes is given. this is useful in case of
		fine-tuning
	"""

	class meta:
		classifier_layers = ["fc6", "fc7", "fc8"]
		conv_map_layer = "conv5_4"
		feature_layer = "fc7"
		feature_size = 4096
		n_conv_maps = 512
		input_size = 224
		mean = np.array([103.939, 116.779, 123.68], dtype=np.float32).reshape(3,1,1)
		prepare_func = prepare

	@staticmethod
	def pooling(x):
		return F.max_pooling_2d(x, ksize=2, stride=2)

	def init_layers(self, n_classes, **kwargs):
		self.conv3_4 = L.Convolution2D(256, 256, 3, 1, 1)
		self.conv4_4 = L.Convolution2D(512, 512, 3, 1, 1)
		self.conv5_4 = L.Convolution2D(512, 512, 3, 1, 1)


	@property
	def _links(self):
		links = [
			('conv1_1',  [self.conv1_1, F.relu]),
			('conv1_2',  [self.conv1_2, F.relu]),
			('pool1',    [VGG19Layers.pooling]),
			('conv2_1',  [self.conv2_1, F.relu]),
			('conv2_2',  [self.conv2_2, F.relu]),
			('pool2',    [VGG19Layers.pooling]),
			('conv3_1',  [self.conv3_1, F.relu]),
			('conv3_2',  [self.conv3_2, F.relu]),
			('conv3_3',  [self.conv3_3, F.relu]),
			('conv3_4',  [self.conv3_4, F.relu]),
			('pool3',    [VGG19Layers.pooling]),
			('conv4_1',  [self.conv4_1, F.relu]),
			('conv4_2',  [self.conv4_2, F.relu]),
			('conv4_3',  [self.conv4_3, F.relu]),
			('conv4_4',  [self.conv4_4, F.relu]),
			('pool4',    [VGG19Layers.pooling]),
			('conv5_1',  [self.conv5_1, F.relu]),
			('conv5_2',  [self.conv5_2, F.relu]),
			('conv5_3',  [self.conv5_3, F.relu]),
			('conv5_4',  [self.conv5_4, F.relu]),
			('pool5',    [VGG19Layers.pooling]),
		]

		if all([hasattr(self, attr) for attr in ["fc6", "fc7", "fc8"]]):
			links += [
				('fc6',      [self.fc6, F.relu, F.dropout]),
				('fc7',      [self.fc7, F.relu, F.dropout]),
				('fc8',      [self.fc8]),
				('prob',     [F.softmax]),
			]
		return links
