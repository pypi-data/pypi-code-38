import cv2, pyforms
from confapp import conf

if conf.PYFORMS_MODE=='GUI':
	from AnyQt.QtWidgets import QFileDialog
	from AnyQt import _api
class ImportExportImage(object):


	def create_popupmenu_actions(self):
		
		self.tree.add_popup_menu_option(
			label='Import', 
			function_action=self.__import_image_window, 
			item=self.treenode, icon=conf.PYFORMS_ICON_EVENTTIMELINE_IMPORT
		)

		#self._value_import_window = GenericCsvParserDialog(['Frame', 'Value'])
		#self._value_import_window.load_file_event = self.__import_data_event

		self.tree.add_popup_menu_option("-", item=self.treenode)
		super(ImportExportImage,self).create_popupmenu_actions()

	def __import_image_window(self):
		value = QFileDialog.getOpenFileName(self, 'Select an image')
		value = value[0] if _api.USED_API == _api.QT_API_PYQT5 else str(value)
		
		self.image = cv2.imread(value)