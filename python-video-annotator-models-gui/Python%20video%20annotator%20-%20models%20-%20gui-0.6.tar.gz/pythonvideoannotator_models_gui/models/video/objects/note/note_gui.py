import csv, cv2, os
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo
from pyforms.controls import ControlLabel
from pyforms.controls import ControlText
from pyforms.controls import ControlTextArea
from pythonvideoannotator_models.models.video.objects.note import Note
from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path

class NoteGUI(IModelGUI, Note, BaseWidget):

	def __init__(self, video):
		IModelGUI.__init__(self)
		Note.__init__(self, video)
		BaseWidget.__init__(self, 'Note', parent_win=video)
		
		self._removeimg = ControlButton('Remove')
		self._text 		= ControlTextArea('Note', self._note)

		
		self.formset = [
			'_name', 			
			'_removeimg',
			'_text'
		]

		self._removeimg.value = self.__remove_image_event
		self._removeimg.icon = conf.ANNOTATOR_ICON_REMOVE
		
		self._text.changed_event = self.__note_changed_event

		self.create_tree_nodes()


	######################################################################
	### EVENTS ###########################################################
	######################################################################

	def on_click(self, event, x, y):
		pass

	def __note_changed_event(self):
		self._note= self._text.value

	######################################################################
	### OBJECT FUNCTIONS #################################################
	######################################################################

	def draw(self, frame, frame_index): pass
		
	######################################################################
	### CLASS FUNCTIONS ##################################################
	######################################################################

	def create_tree_nodes(self):

		self.treenode = self.tree.create_child(self.name, icon=conf.ANNOTATOR_ICON_PICTURE, parent=self.video.treenode)
		self.treenode.win = self

		self.tree.add_popup_menu_option(
			label='Remove', 
			function_action=self.__remove_image_event, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_DELETE
		)



	######################################################################
	### EVENTS ###########################################################
	######################################################################

	def __remove_image_event(self):
		item = self.tree.selected_item
		if item is not None: self.video -= item.win
	
	def double_clicked_event(self):
		#cv2.imshow(self.name, self.image)
		self.mainwindow.player.frame = self.image


	######################################################################
	### PROPERTIES #######################################################
	######################################################################
	
	@property
	def mainwindow(self): 	return self.video.mainwindow
	@property
	def tree(self): 		return self.video.tree
	
	@property 
	def parent_treenode(self):  return self.video.treenode

	
	@property
	def note(self): 		return self._text.value
	@note.setter
	def note(self, value): 	self._text.value = value