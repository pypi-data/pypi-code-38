from forecastlib.libs.ModelSerializer import ModelSerializer


class ForecastModel(object):
	def __init__(self, model, feature_scaler, label_scaler, features):
		self.features = features
		self.feature_scaler = feature_scaler
		self.label_scaler = label_scaler
		self.model = model

	def predict(self, x):
		x_featured = x[self.features].copy()
		x_scaled = self.feature_scaler.transform(x_featured)
		print(x_scaled)
		y_scaled = self.model.predict(x_scaled)
		return self.label_scaler.inverse_transform(y_scaled.reshape(-1, 1))

	def save(self, path: str):
		ModelSerializer.save_keras_model(self.model, path)
		ModelSerializer.save_scaler(self.label_scaler, path, "label")
		ModelSerializer.save_scaler(self.feature_scaler, path, "features")
		ModelSerializer.save_features(self.features, path)

	@staticmethod
	def load(path: str):
		model = ModelSerializer.load_keras_model(path)
		features = ModelSerializer.load_features(path)
		feature_scaler = ModelSerializer.load_scaler(path, "features")
		label_scaler = ModelSerializer.load_scaler(path, "label")

		return ForecastModel(model, feature_scaler, label_scaler, features)

