import cv2
from confapp import conf
from pythonvideoannotator_module_distances.distances_window import DistancesWindow


class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()
		self.distances_window = DistancesWindow(self)

		self.mainmenu[1]['Modules'].append(
			{'Distances': self.distances_window.show, 'icon':conf.ANNOTATOR_ICON_DISTANCES },			
		)