import cv2
from confapp import conf
from pythonvideoannotator_module_smoothpaths.smoothpaths_window import SmoothPathsWindow


class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()
		self.smoothpaths_window = SmoothPathsWindow(self)

		self.mainmenu[1]['Modules'].append(
			{'Smooth': self.smoothpaths_window.show, 'icon':conf.ANNOTATOR_ICON_SMOOTH },			
		)