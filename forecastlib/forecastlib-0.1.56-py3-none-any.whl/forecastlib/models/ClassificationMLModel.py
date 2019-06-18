from forecastlib.libs.ModelSerializer import ModelSerializer


class ClassificationMLModel(object):
	def __init__(self, model, features):
		self.features = features
		self.model = model

	def predict(self, x):
		data = x[self.features]
		return self.model.predict(data)

	def save(self, path: str):
		ModelSerializer.save_ml_model(self.model, path)
		ModelSerializer.save_features(self.features, path)

	@staticmethod
	def load(path: str):
		model = ModelSerializer.load_ml_model(path)
		features = ModelSerializer.load_features(path)

		return ClassificationMLModel(model, features)
