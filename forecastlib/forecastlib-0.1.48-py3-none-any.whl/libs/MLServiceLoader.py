import os.path

from azureml.core.model import Model
from azureml.core import Workspace


class MLServiceLoader(object):
	loadedModels = {}

	def __init__(self, ws: Workspace):
		self.ws = ws

	def download(self, model_name: str, version: int = None, force: bool = False):
		models = Model.list(self.ws, model_name)

		if version is None:
			selected_model = max(models, key=lambda item: item.version)
			version = selected_model.version
		else:
			selected_model = next(x for x in models if x.version == version)

		self.loadedModels[selected_model.name] = "Version: {:.0f} ({})".format(selected_model.version, selected_model.description)

		model_path = "./azureml-models" + os.path.sep + model_name + os.path.sep + str(version) + os.path.sep + model_name

		if force or not os.path.exists(model_path):
			return Model.get_model_path(model_name, version, self.ws)

		return model_path

