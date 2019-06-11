from confapp import conf
from pyforms_gui.dialogs.generic_csv_parser import GenericCsvParserDialog

class ImportExportValue(object):


	def create_popupmenu_actions(self):
		
		self.tree.add_popup_menu_option(
			label='Import', 
			function_action=self.__show_import_data_window, 
			item=self.treenode, icon=conf.PYFORMS_ICON_EVENTTIMELINE_IMPORT
		)

		self._value_import_window = GenericCsvParserDialog(['Frame', 'Value'])
		self._value_import_window.load_file_event = self.__import_data_event

		self.tree.add_popup_menu_option("-", item=self.treenode)
		super(ImportExportValue,self).create_popupmenu_actions()


	def __show_import_data_window(self):
		self._value_import_window.show()

	def __import_data_event(self):
		for frame, value in self._value_import_window:
			frame = int(frame)
			value = None if value=='None' or value.strip()=='' else float(value)
			self.set_value(frame, value)


		self._value_import_window.hide()