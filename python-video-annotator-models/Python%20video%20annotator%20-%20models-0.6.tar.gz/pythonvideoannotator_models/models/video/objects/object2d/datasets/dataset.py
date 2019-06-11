import os, simplejson as json
from pythonvideoannotator_models.models.imodel import IModel

class Dataset(IModel):

	FACTORY_FUNCTION = ''

	def __init__(self, object2d):		
		super(IModel, self).__init__()

		object2d   		+= self
		self.object2d   = object2d
		self.name 		= 'dataset({0})'.format(len(object2d.datasets))


	@property
	def object2d(self): return self._object2d
	@object2d.setter
	def object2d(self,value): self._object2d = value

	@property
	def directory(self): return os.path.join( self.object2d.directory, 'datasets',self.name)


	

	def save(self, data, path=None):
		data['factory-function'] = self.FACTORY_FUNCTION
		conf_path = os.path.join(path, 'dataset.json')
		with open(conf_path, 'w') as outfile: json.dump(data, outfile)
		return super(Dataset, self).save(data, path)

	def load(self, data, path=None):
		self.name = os.path.basename(path)
		return super(Dataset, self).load(data, path)
