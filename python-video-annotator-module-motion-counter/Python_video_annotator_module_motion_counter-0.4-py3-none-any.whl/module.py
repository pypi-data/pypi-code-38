import cv2
from confapp import conf
from pythonvideoannotator_module_motioncounter.motion_counter import MotionCounter


class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()
		self.motion_window = MotionCounter(self)

		self.mainmenu[1]['Modules'].append(
			{'Motion': self.motion_window.show, 'icon':conf.ANNOTATOR_ICON_MOTION },			
		)

	def video_changed_event(self):
		super(Module, self).video_changed_event()
		self.motion_window.video_filename = self._video.value



	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	