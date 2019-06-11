import cv2
from confapp import conf
from pythonvideoannotator_module_virtualobjectgenerator.videosexporter.videosexporter_gui import VideosExporterGui


class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()


		self.virtualobjectgenerator_window = VideosExporterGui(self)

		self.mainmenu[1]['Modules'].append('-')

		self.mainmenu[1]['Modules'].append(
			{'Export videos': self.virtualobjectgenerator_window.show, 'icon':conf.ANNOTATOR_ICON_MOVIE },			
		)



	
	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	
	def save(self, data, project_path=None):
		data = super(Module, self).save(data, project_path)
		data['virtualobjectgenerator-settings'] = self.virtualobjectgenerator_window.save_form({})
		return data

	def load(self, data, project_path=None):
		super(Module, self).load(data, project_path)
		if 'virtualobjectgenerator-settings' in data: self.virtualobjectgenerator_window.load_form(data['virtualobjectgenerator-settings'])
		