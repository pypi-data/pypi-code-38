from confapp import conf

from pyforms_gui.dialogs.generic_csv_parser import GenericCsvParserDialog

class ImportExportPath(object):


	def create_popupmenu_actions(self):		
		self.tree.add_popup_menu_option(
			label='Import', 
			function_action=self.__show_import_data_window, 
			item=self.treenode, icon=conf.PYFORMS_ICON_EVENTTIMELINE_IMPORT
		)

		self._value_import_window = GenericCsvParserDialog(['Frame', 'X', 'Y'])
		self._value_import_window.load_file_event = self.__import_data_event

		self.tree.add_popup_menu_option('-', item=self.treenode)
		super(ImportExportPath,self).create_popupmenu_actions()


	def __show_import_data_window(self):
		self._value_import_window.show()

	def __import_data_event(self):

		try:
			for frame, x, y in self._value_import_window:
				frame = int(frame)
				x = None if x=='None' or x.strip()=='' else float(x)
				y = None if y=='None' or y.strip()=='' else float(y)
				self.set_position(frame, x, y)
		except Exception as e:
			self.message(str(e))
                        
		self._value_import_window.hide()