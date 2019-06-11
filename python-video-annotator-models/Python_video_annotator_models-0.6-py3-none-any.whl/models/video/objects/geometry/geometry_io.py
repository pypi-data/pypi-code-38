import os, cv2, simplejson as json
from send2trash import send2trash
from pythonvideoannotator_models.models.video.objects.geometry.geometry_base import GeometryBase

class GeometryIO(GeometryBase):

	FACTORY_FUNCTION = 'create_geometry'

	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	def save(self, data, geometry_path=None):
		data = super(GeometryIO, self).save(data, geometry_path)

		filepath = os.path.join(geometry_path, 'data.geo')

		with open(filepath, 'w') as outfile: 
			json.dump(self._geometry, outfile)
		
		return data


	def load(self, data, geometry_path=None):
		data = super(GeometryIO, self).load(data, geometry_path)

		filepath = os.path.join(geometry_path, 'data.geo')

		with open(filepath, 'rb') as infile: 
			self._geometry = json.load(infile)
		
		return data