import pyforms, cv2, base64, numpy as np
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlEmptyWidget
from mcvapi.masks.polygons_mask import PolygonsMask as Class
from pythonvideoannotator_models_gui.models.video.objects.geometry import Geometry

from pythonvideoannotator_models_gui.dialogs import ObjectsDialog

class PolygonsMask(Class, BaseWidget):
	
	def __init__(self, **kwargs):
		BaseWidget.__init__(self, 'Polygons Mask')
		Class.__init__(self, **kwargs)

		try:
			self.layout().setContentsMargins(10, 5, 10, 5)
			self.setMinimumHeight(150)
		except:
			pass

		self._panel	= ControlEmptyWidget('Panel', default=ObjectsDialog() )
		self._panel.value.objects_filter = lambda x: isinstance(x, Geometry)
		self._panel.value.objects_changed_event = self.__objects_changed_event

	def destroy(self, destroyWindow = True, destroySubWindows = True):
		self._panel.value.destroy(destroyWindow, destroySubWindows)
		super(PolygonsMask, self).destroy(destroyWindow, destroySubWindows)

	def __objects_changed_event(self):
		polygons_list = []
		for video, polygons_set in self._panel.value.selected_data:
			if video.video_capture==self._video: 
				for polygons in polygons_set:
					polygons_list += [p for l, p in polygons.geometry]
				break
		self._param_polygonsmask_mask = None
		self._param_polygonsmask_polys = np.int32(polygons_list)

	@property
	def video(self): return None
	@video.setter 
	def video(self, value):
		self._video = value
		self.__objects_changed_event()



if __name__ == '__main__': 
	pyforms.start_app(PolygonsMask)