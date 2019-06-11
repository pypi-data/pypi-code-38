import os, simplejson as json
from send2trash import send2trash
from pythonvideoannotator_models.models.video.objects.object2d.object2d_base import Object2dBase
from pythonvideoannotator_models.utils.tools import list_folders_in_path

class Object2dIO(Object2dBase):

	FACTORY_FUNCTION = 'create_object'

	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	def save(self, data, object2d_path=None):
		data = super(Object2dIO, self).save(data, object2d_path)

		datasets_path = os.path.join(object2d_path, 'datasets')
		if not os.path.exists(datasets_path): os.makedirs(datasets_path)
		
		datasets = []
		for dataset in self._datasets:
			dataset_path = os.path.join(datasets_path, dataset.name)
			if not os.path.exists(dataset_path): os.makedirs(dataset_path)
			dataset.save({}, dataset_path)
			datasets.append(dataset.directory)
		
		for dataset_path in list_folders_in_path(datasets_path):
			if dataset_path not in datasets:
				if os.path.exists(dataset_path):
					send2trash(dataset_path)

		return data

	def load(self, data, object2d_path=None):
		data = super(Object2dIO, self).save(data, object2d_path)

		dirname = os.path.basename(object2d_path)
		
		datasets_path = os.path.join(object2d_path, 'datasets')
		
		for dataset_path in list_folders_in_path(datasets_path):
			name		= os.path.basename(dataset_path)
			conf_path 	= os.path.join(dataset_path, 'dataset.json')

			with open(conf_path, 'r') as infile:
				dataset_conf = json.load(infile)
				func = getattr(self, dataset_conf['factory-function'])
				dataset = func()
				dataset.name = name
				dataset.load(dataset_conf, dataset_path)