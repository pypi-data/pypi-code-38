from pyforms.basewidget import BaseWidget
from pythonvideoannotator_module_tracking.module_mcvapi.blobs.sort_paths import SortPaths as Class


class SortPaths(Class, BaseWidget):
	
	def __init__(self, **kwargs):
		BaseWidget.__init__(self, 'Sort paths')
		Class.__init__(self, **kwargs)

		try:
			self.layout().setContentsMargins(10, 5, 10, 5)
			self.setMinimumHeight(55)
		except:
			pass