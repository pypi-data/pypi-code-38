import chainer
import chainer.links as L

from .base import BaseClassifier

class Classifier(BaseClassifier):
	"""
		model wrapper, that is adapted for the DSL of
		the pretrained models in chainer_addons
	"""

	def __call__(self, X, y):
		pred = self.model(X, layer_name=self.layer_name)
		loss, accu = self.loss(pred, y), self.model.accuracy(pred, y)

		chainer.report({
			"loss": loss.data,
			"accuracy": accu.data,
		}, self)
		return loss

class RNNClassifier(BaseClassifier):
	def __init__(self, model, layer_name=None, rnn_cls=L.LSTM, units=2048, **kwargs):
		layer_name = layer_name or model.meta.feature_layer
		super(RNNClassifier, self).__init__(model, layer_name, **kwargs)
		with self.init_scope():
			self.rnn = rnn_cls(model.meta.feature_size, units)
			self.clf = L.Linear(units, model.clf_layer.W.shape[0])

	def __call__(self, X, y):
		assert X.ndim == 5, "Incorrect input data format!"

		self.rnn.reset_state()

		for part in X.transpose(1,0,2,3,4):
			part_feat = self.model(part, layer_name=self.layer_name)
			feat = self.rnn(part_feat)

		pred = self.clf(feat)
		loss, accu = self.loss(pred, y), self.model.accuracy(pred, y)

		chainer.report({
			"loss": loss.data,
			"accuracy": accu.data,
		}, self)
		return loss
