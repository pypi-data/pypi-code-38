import os,simplejson as  json
from pythonvideoannotator_models.models.imodel import IModel


class VideoObject(IModel):

	FACTORY_FUNCTION = ''

	def save(self, data, path=None):
		data['factory-function'] = self.FACTORY_FUNCTION
		conf_path = os.path.join(path, 'dataset.json')
		with open(conf_path, 'w') as outfile: json.dump(data, outfile)
		return super(VideoObject, self).save(data, path)

	def load(self, data, path=None):
		self.name = os.path.basename(path)
		return super(VideoObject, self).load(data, path)

	######################################################################
	### PROPERTIES #######################################################
	######################################################################


	@property
	def video(self): return self._video
	@video.setter
	def video(self, value): self._video = value

	@property 
	def video_capture(self):  return self.video.video_capture