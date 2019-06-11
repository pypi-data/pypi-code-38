import cv2
from confapp import conf
from pythonvideoannotator_module_importexport.export_window import ExportWindow


class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()
		self.importexport_window = ExportWindow(self)

		self.mainmenu[1]['Modules'].append(
			{'Export data': self.__show_import_export_window, 'icon': conf.PYFORMS_ICON_EVENTTIMELINE_EXPORT },			
		)

	def __show_import_export_window(self):
		self.importexport_window.show()
		self.importexport_window.project = self._project
