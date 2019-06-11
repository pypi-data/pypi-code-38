from forecastlib.libs.ModelSerializer import ModelSerializer


class ClassificationNNModel(object):
	def __init__(self, model, features, scaler):
		self.features = features
		self.model = model
		self.scaler = scaler

	def predict(self, x):
		data = x[self.features]
		x_scaled = self.scaler.transform(data)
		y_pred = self.model.predict(x_scaled)
		y_pred =(y_pred>0.5)

		return y_pred

	def save(self, path: str):
		ModelSerializer.save_keras_model(self.model, path)
		ModelSerializer.save_scaler(self.scaler, path)
		ModelSerializer.save_features(self.features, path)

	@staticmethod
	def load(path: str):
		model = ModelSerializer.load_keras_model(path)
		features = ModelSerializer.load_features(path)
		scaler = ModelSerializer.load_scaler(path)

		return ClassificationNNModel(model, features, scaler)
