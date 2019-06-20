"""
here you can find some model definitions or modificated versions
of present models in chainer (eg. VGG19)
"""

from functools import partial

from .alexnet import AlexNet
from .vgg import VGG19Layers
from .resnet import ResnetLayers, Resnet35Layers
from .inception import InceptionV3
from .classifier import Classifier, RNNClassifier

from chainer_addons.utils.imgproc import generic_prepare, generic_tf_prepare

from cvargparse.utils.enumerations import BaseChoiceType

class ModelType(BaseChoiceType):
	ResNet = ResnetLayers
	VGG19 = VGG19Layers
	Inception = InceptionV3

	Default = ResnetLayers

	def __call__(self, *args, **kwargs):
		"""
			Initializes new model instance
		"""
		model_cls = self.value
		model = model_cls(*args, **kwargs)
		return model

	@staticmethod
	def new(model_type, input_size, pooling, pooling_params={}, aux_logits=False):

		model_type = ModelType[model_type]
		kwargs = dict(
			pooling=pooling,
			pooling_params=pooling_params
		)

		if model_type == ModelType.Inception:
			kwargs["aux_logits"] = aux_logits

		if input_size > 0:
			model_type.value.meta.input_size = input_size

		return model_type(**kwargs)



class PrepareType(BaseChoiceType):
	MODEL = 0
	CUSTOM = 1
	TF = 2

	Default = CUSTOM

	def __call__(self, model):
		"""
			Initializes image preprocessing function
		"""

		if self == PrepareType.MODEL:
			return model.meta.prepare_func

		elif self == PrepareType.CUSTOM:
			return partial(generic_prepare,
				size=model.meta.input_size)

		elif self == PrepareType.TF:
			return generic_tf_prepare(
				size=model.meta.input_size,
				from_path=False)

