#! /usr/bin/python2
# -*- coding: utf-8 -*-
import os
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlButton
from pyforms.controls import ControlTree
from pyforms.controls import ControlList
from pyforms.controls import ControlEmptyWidget
from pyforms.dialogs  import CsvParserDialog

from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI
from pythonvideoannotator_models.models import Project
from pythonvideoannotator_models_gui.models.video import Video
from pythonvideoannotator_models_gui.models.video.objects.image import Image


class ProjectGUI(IModelGUI, Project, BaseWidget):
	"""Application form"""

	_project = None

	def __init__(self, parent=None):
		IModelGUI.__init__(self)
		Project.__init__(self)
		BaseWidget.__init__(self, 'Project window', parent_win=parent)
		
		conf.PROJECT = self
		self._parent = parent
		
		self._tree 			= ControlTree('')
		self._addvideo 		= ControlButton('Add video')
		self._removevideo 	= ControlButton('Remove video')
		self.formset 		= [
			'_tree', 
			'_addvideo',
		]
	
		## set controls ##########################################################
		self._tree.show_header  = False
		self._addvideo.value 	= self.__create_video_event

		self._addvideo.icon 	= conf.ANNOTATOR_ICON_ADD

		self.tree.item_double_clicked_event    = self.tree_item_double_clicked_event
		self.tree.item_selection_changed_event = self.tree_item_selection_changed_event
		

	######################################################################################
	#### FUNCTIONS #######################################################################
	######################################################################################

	def create_video(self): return Video(self)

	######################################################################################
	#### GUI EVENTS ######################################################################
	######################################################################################

	def key_release_event(self, evt):
		if self._tree.selected_row_index is not None:
			obj = self._tree.selected_item.win
			obj.key_release_event(evt)

	def tree_item_double_clicked_event(self, item):
		if isinstance(item.win, Image): item.win.double_clicked_event()

	def tree_item_selection_changed_event(self):
		self.mainwindow.player.refresh()
		if self.tree.selected_item is not None and hasattr(self.tree.selected_item,'win'):
			self.mainwindow.details = self.tree.selected_item.win
			self.mainwindow.details.show()
	

	def __create_video_event(self):
		video = self.create_video()
		video.choose_file()

	def __remove_video_event(self):
		 item = self.tree.selected_item
		 if item: self -= item.win

	######################################################################################
	#### PUBLIC FUNCTIONS ################################################################
	######################################################################################

	def __sub__(self, obj):
		super(ProjectGUI, self).__sub__(obj)
		if isinstance(obj, Video): self._tree -= obj.treenode
		return self

	def player_on_drag(self, p1, p2):
		if self._tree.selected_row_index is not None:
			obj = self._tree.selected_item.win
			obj.on_drag(p1, p2)

	def player_on_end_drag(self, p1, p2):
		if self._tree.selected_row_index is not None:
			obj = self._tree.selected_item.win
			obj.on_end_drag(p1, p2)
		
	def player_on_click(self, event, x, y):
		if self._tree.selected_row_index is not None:
			obj = self._tree.selected_item.win
			obj.on_click(event, x, y)

	def player_on_double_click(self, event, x, y):
		if self._tree.selected_row_index is not None:
			obj = self._tree.selected_item.win
			obj.on_double_click(event, x, y)

	def draw(self, frame, frame_index):
		if self._tree.selected_row_index is not None:
			obj = self._tree.selected_item.win
			obj.draw(frame, frame_index)

	def save(self, data, project_path=None):
		data = super(ProjectGUI, self).save(data, project_path)
		timeline_path = os.path.join(project_path, 'timeline.csv')
		self.mainwindow.timeline.export_csv_file(timeline_path)
		return data

	def load(self, data, project_path=None):
		super(ProjectGUI, self).load(data, project_path)
		timeline_path = os.path.join(project_path, 'timeline.csv')
		if os.path.isfile(timeline_path):
			self.mainwindow.timeline.import_csv_file(timeline_path)
		return data
		
	######################################################################################
	#### PROPERTIES ######################################################################
	######################################################################################

	@property
	def mainwindow(self): 	return self._parent

	@property
	def tree(self): 	return self._tree

	@property
	def objects(self):  	return [item.win for item in self._tree.value]


	@property
	def name(self): return self.directory
	@name.setter
	def name(self, value): pass
		