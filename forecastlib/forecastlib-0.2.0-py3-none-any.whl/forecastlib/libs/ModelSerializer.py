import json
import os
from joblib import dump, load

from keras.models import model_from_json


class ModelSerializer(object):

	@staticmethod
	def save_keras_model(model, folder: str, name: str = "model"):
		model.save(folder + os.path.sep + ModelSerializer.get_model_filename(name))
		architecture = model.to_json()
		with open(folder + os.path.sep + ModelSerializer.get_model_architecture_filename(name), 'w') as f:
			f.write(architecture)
		model.save_weights(folder + os.path.sep + ModelSerializer.get_model_weights_filename(name))

	@staticmethod
	def load_keras_model(folder: str, model_name="model"):
		model_arch_file = folder + os.path.sep + ModelSerializer.get_model_architecture_filename(model_name)
		model_weights_file = folder + os.path.sep + ModelSerializer.get_model_weights_filename(model_name)

		with open(model_arch_file) as json_file:
			model = model_from_json(json_file.read())
		model.load_weights(model_weights_file)
		model._make_predict_function()

		return model

	@staticmethod
	def save_ml_model(model, folder: str, model_name: str = "model"):
		with open(folder + os.path.sep + ModelSerializer.get_model_filename(model_name), 'wb') as outfile:
			dump(model, outfile)

	@staticmethod
	def load_ml_model(folder: str, model_name: str = "model"):
		with open(folder + os.path.sep + ModelSerializer.get_model_filename(model_name), "rb") as dump_file:
			model = load(dump_file)
			return model

	@staticmethod
	def save_scaler(scaler, folder: str, name: str = "model"):
		from sklearn.externals import joblib
		joblib.dump(scaler, folder + os.path.sep + ModelSerializer.get_scaler_filename(name))

	@staticmethod
	def load_scaler(folder: str, model_name="model"):
		model_scaler_file = folder + os.path.sep + ModelSerializer.get_scaler_filename(model_name)

		scaler = load(model_scaler_file)

		return scaler


	@staticmethod
	def save_features(features, folder: str, name: str = "model"):
		with open(folder + os.path.sep + ModelSerializer.get_feature_filename(name), 'w') as outfile:
			json.dump(features, outfile)

	@staticmethod
	def load_features(folder: str, model_name="model"):
		feature_file = folder + os.path.sep + ModelSerializer.get_feature_filename(model_name)

		with open(feature_file) as json_file:
			features = json.load(json_file)

		return features


	@staticmethod
	def get_feature_filename(name="model"):
		return name + ".features.json"

	@staticmethod
	def get_model_filename(name="model"):
		return name + ".model.h5"

	@staticmethod
	def get_model_architecture_filename(name="model"):
		return name + ".arch.json"

	@staticmethod
	def get_model_weights_filename(name="model"):
		return name + ".weights.h5"

	@staticmethod
	def get_scaler_filename(name="model"):
		return name + ".scaler.dump"
