

class ClassificationModel(object):
	def __init__(self, model, features):
		self.features = features
		self.model = model

	def predict(self, x):
		data = x[self.features]
		return self.model.predict(data)

