import pyforms, cv2, base64, numpy as np
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlEmptyWidget
from mcvgui.filters.background_subtract import BackgroundSubtract as Class
from pythonvideoannotator_models_gui.models.video.objects.image import Image

from pythonvideoannotator_models_gui.dialogs import ObjectsDialog

class BackgroundSubtract(Class, BaseWidget):
	
	def __init__(self, **kwargs):
		BaseWidget.__init__(self, 'Polygons Mask')
		Class.__init__(self, **kwargs)

		try:
			self.layout().setContentsMargins(10, 5, 10, 5)
			self.setMinimumHeight(230)
		except:
			pass

		self._panel	= ControlEmptyWidget('Panel', default=ObjectsDialog() )
		self._panel.value.objects_filter = lambda x: isinstance(x, Image)
		self._panel.value.objects_changed_event = self.__objects_changed_event

		self.formset = [
			'_field_background_subtract_threshold',
			'_panel'
		]

	def destroy(self, destroyWindow = True, destroySubWindows = True):
		self._panel.value.destroy(destroyWindow, destroySubWindows)
		super(BackgroundSubtract, self).destroy(destroyWindow, destroySubWindows)

	def __objects_changed_event(self):
		for video, images in self._panel.value.selected_data:
			for image in images:
				self._param_backgroundsubtract_image = image.image




if __name__ == '__main__': 
	pyforms.start_app(PolygonsMask)