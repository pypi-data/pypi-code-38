import csv, cv2, os
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo
from pyforms.controls import ControlLabel
from pyforms.controls import ControlText

from pythonvideoannotator_models.models.video.objects.object2d import Object2D
from pythonvideoannotator_models_gui.dialogs import Dialog
from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.value import Value

if conf.PYFORMS_MODE=='GUI':
	from AnyQt.QtWidgets import QInputDialog

class Object2dGUI(IModelGUI, Object2D, BaseWidget):

	def __init__(self, video):
		IModelGUI.__init__(self)
		Object2D.__init__(self, video)
		BaseWidget.__init__(self, '2D Object', parent_win=video)
		
		self._addpath 		= ControlButton('Add path')
		self._addcontours	= ControlButton('Add contours')
		self._addvalues		= ControlButton('Add values')
		self._removeobj  	= ControlButton('Remove')
		

		self.formset = [
			'_name', 			
			#('_addpath', '_addcontours'),
			#'_addvalues',
			'_removeobj',
			' '
		]

		self._addpath.icon 	= conf.ANNOTATOR_ICON_ADD
		self._removeobj.icon 	= conf.ANNOTATOR_ICON_REMOVE		
		self._addcontours.icon 	= conf.ANNOTATOR_ICON_CONTOUR		
		self._addvalues.icon 	= conf.ANNOTATOR_ICON_CONTOUR

		self._addpath.value = self.create_path
		self._addcontours.value = self.create_contours
		self._addvalues.value = self.create_value
		self._removeobj.value = self.__remove_object

		self.create_tree_nodes()


		

	######################################################################
	### FUNCTIONS ########################################################
	######################################################################




	def __sub__(self, obj):
		super(Object2dGUI, self).__sub__(obj)
		if isinstance(obj, Path): self.treenode.removeChild(obj.treenode)
		if isinstance(obj, Contours): self.treenode.removeChild(obj.treenode)
		if isinstance(obj, Value): self.treenode.removeChild(obj.treenode)		
		return self

			

	def create_tree_nodes(self):
		self.treenode = self.tree.create_child(self.name, icon=conf.ANNOTATOR_ICON_OBJECT, parent=self.video.treenode)
		self.treenode.win = self

		self.tree.add_popup_menu_option(
			label='Add a path', 
			function_action=self.create_path, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_PATH
		)
		self.tree.add_popup_menu_option(
			label='Add contours', 
			function_action=self.create_contours, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_CONTOUR
		)
		self.tree.add_popup_menu_option(
			label='Add a value', 
			function_action=self.create_value, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_INFO
		)

		self.tree.add_popup_menu_option(
			label='Import value from timeline', 
			function_action=self.__import_value_from_timeline, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_INFO
		)

		self.tree.add_popup_menu_option('-',item=self.treenode)
		self.tree.add_popup_menu_option('-', item=self.treenode)
		self.tree.add_popup_menu_option(
			label='Remove', 
			function_action=self.__remove_object, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_DELETE
		)
		
	def __remove_object(self):
		item = self.tree.selected_item
		if item is not None: self.video -= item.win

	def create_path(self): return Path(self)
	def create_contours(self): 	return Contours(self)
	def create_value(self): return Value(self)

	######################################################################
	### EVENTS ###########################################################
	######################################################################

	def __import_value_from_timeline(self):
		timeline = self.mainwindow._time
		graphs = timeline.graphs

		item, ok = QInputDialog.getItem(self, 
			"Select the value to import", 'Value', 
			[str(graph) for graph in graphs], 
			editable=False
		)
		if ok:
			for graph in graphs:
				if str(item)==str(graph):
					v = self.create_value()
					v.name = graph.name
					for i in range(len(graph)):
						v.set_value(i, graph[i])


	def on_double_click(self, event, x, y):
		for dataset in self.datasets: dataset.on_double_click(event, x, y)

	def on_click(self, event, x, y):
		for dataset in self.datasets: dataset.on_click(event, x, y)

	def draw(self, frame, frame_index):
		for dataset in self.datasets: dataset.draw(frame, frame_index)
	

	######################################################################
	### PROPERTIES #######################################################
	######################################################################

	@property
	def mainwindow(self): 	return self.video.mainwindow
	@property
	def tree(self): 		return self.video.tree
	@property
	def video_capture(self):return self.video.video_capture

	
	@property 
	def parent_treenode(self):  return self.video.treenode
