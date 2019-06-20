import numpy as np
import chainer
import chainer.links as L
import chainer.functions as F

from chainer.serializers import npz
from chainer.links.model.vision.resnet import prepare, BuildingBlock
from functools import partial

from .base import PretrainedModelMixin

class ResnetMixin(PretrainedModelMixin):

	@property
	def _links(self):
		links = [
				('conv1', [self.conv1, self.bn1, F.relu]),
				('pool1', [partial(F.max_pooling_2d, ksize=3, stride=2)]),
				('res2', [self.res2]),
				('res3', [self.res3]),
				('res4', [self.res4]),
				('res5', [self.res5]),
				('pool5', [self.pool])]
		if hasattr(self, "fc6"):
			links +=[
				('fc6', [self.fc6]),
				('prob', [F.softmax]),
			]

		return links


class ResnetLayers(ResnetMixin, L.ResNet50Layers):

	class meta:
		classifier_layers = ["fc6"]
		conv_map_layer = "res5"
		feature_layer = "pool5"
		feature_size = 2048
		n_conv_maps = 2048
		input_size = 448
		mean = np.array([103.063,  115.903,  123.152], dtype=np.float32).reshape(3,1,1)

		@staticmethod
		def prepare_func(x, size, *args, **kwargs):
			return prepare(x, size)

	def init_layers(self, n_classes, **kwargs):
		pass


class Resnet35Layers(ResnetMixin, chainer.Chain):

	class meta:
		classifier_layers = ["fc6"]
		conv_map_layer = "res5"
		feature_layer = "pool5"
		feature_size = 2048
		n_conv_maps = 2048
		input_size = 448
		mean = np.array([103.063,  115.903,  123.152], dtype=np.float32).reshape(3,1,1)

		prepare_func = prepare


	def init_layers(self, n_classes, **kwargs):
		self.conv1 = L.Convolution2D(3, 64, 7, 2, 3, **kwargs)
		self.bn1 = L.BatchNormalization(64)
		self.res2 = BuildingBlock(2, 64, 64, 256, 1, **kwargs)
		self.res3 = BuildingBlock(3, 256, 128, 512, 2, **kwargs)
		self.res4 = BuildingBlock(3, 512, 256, 1024, 2, **kwargs)
		self.res5 = BuildingBlock(3, 1024, 512, 2048, 2, **kwargs)
		self.fc6 = L.Linear(2048, n_classes)

	def __call__(self, x,  layer_name=None):
		layer_name = layer_name or self.meta.classifier_layers[-1]
		for key, funcs in self.functions.items():
			for func in funcs:
				x = func(x)
			if key == layer_name:
				return x
