import cv2
from confapp import conf
from pythonvideoannotator_module_backgroundfinder.backgroundfinder_window import BackgroundFinderWindow


class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()


		self.backgroundfinder_window = BackgroundFinderWindow(self)


		self.mainmenu[1]['Modules'].append(
			{'Calculate the video background': self.backgroundfinder_window.show, 'icon':conf.ANNOTATOR_ICON_BACKGROUND },			
		)



	
	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	
	def save(self, data, project_path=None):
		data = super(Module, self).save(data, project_path)
		data['backgroundfinder-settings'] = self.backgroundfinder_window.save_form({})
		return data

	def load(self, data, project_path=None):
		super(Module, self).load(data, project_path)
		if 'backgroundfinder-settings' in data: self.backgroundfinder_window.load_form(data['backgroundfinder-settings'])
		