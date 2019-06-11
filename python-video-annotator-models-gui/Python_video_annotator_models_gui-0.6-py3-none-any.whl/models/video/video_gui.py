#! /usr/bin/python2
# -*- coding: utf-8 -*-
import os, cv2
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlText
from pyforms.controls import ControlFile
from pyforms.controls import ControlButton
from pyforms.controls import ControlLabel


from pythonvideoannotator_models.models.video.objects.video_object import VideoObject
from pythonvideoannotator_models_gui.models.video.objects.image import Image
from pythonvideoannotator_models_gui.models.video.objects.geometry import Geometry
from pythonvideoannotator_models_gui.models.video.objects.note import Note
from pythonvideoannotator_models_gui.models.video.objects.object2d import Object2D
from pythonvideoannotator_models_gui.dialogs import Dialog
from pythonvideoannotator_models.models.video import Video
from pythonvideoannotator_models_gui.models.imodel_gui import IModelGUI

class VideoGUI(IModelGUI, Video, BaseWidget):

	def __init__(self, project):
		IModelGUI.__init__(self)
		Video.__init__(self, project)
		BaseWidget.__init__(self, 'Video window', parent_win=project)

		self._file 			= ControlFile('Video')
		self._addobj 		= ControlButton('Add object')
		self._addimg 		= ControlButton('Add Image')
		self._removevideo  	= ControlButton('Remove')
		self._fps_label 	= ControlLabel('Frames per second')
		self._width_label 	= ControlLabel('Width')
		self._height_label 	= ControlLabel('Height')
		

		self.formset = [
			'_name',
			'_file',
			'_removevideo',
			'_fps_label',
			('_width_label', '_height_label'),
			' '
		]

		self._name.enabled = False

		self._addobj.icon 	 	= conf.ANNOTATOR_ICON_ADD
		self._addimg.icon 	 	= conf.ANNOTATOR_ICON_ADD
		self._removevideo.icon 	= conf.ANNOTATOR_ICON_REMOVE

		self._addobj.value   	 = self.create_object
		self._addimg.value   	 = self.create_image
		

		self._removevideo.value  = self.__remove_video_changed_event
		self._file.changed_event = self.__file_changed_event

		self.treenode = self.tree.create_child('Video', icon=conf.ANNOTATOR_ICON_VIDEO)
		self.treenode.win = self

	def init_form(self):
		if not self._formLoaded:
			self.create_tree_nodes()
		super().init_form()


	#####################################################################################
	########### FUNCTIONS ###############################################################
	#####################################################################################

	def __sub__(self, obj):
		super(VideoGUI, self).__sub__(obj)
		if isinstance(obj, VideoObject): 
			tree = self.project.tree
			tree -= obj.treenode
		return self

	def draw(self, frame, frame_index):
		for obj in self.objects: obj.draw(frame, frame_index)


	def create_tree_nodes(self):
		self.tree.selected_item = self.treenode

		self.tree.add_popup_menu_option(
			label='Add object', 
			function_action=self.create_object, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_OBJECT
		)
		self.tree.add_popup_menu_option(
			label='Add geometry', 
			function_action=self.create_geometry, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_GEOMETRY
		)
		self.tree.add_popup_menu_option(
			label='Add note', 
			function_action=self.create_note, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_NOTE
		)
		self.tree.add_popup_menu_option(
			label='Add image', 
			function_action=self.create_image, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_IMAGE
		)

		self.tree.add_popup_menu_option('-', item=self.treenode)

		self.tree.add_popup_menu_option(
			label='Capture the current frame', 
			function_action=self.__capture_current_frame, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_IMAGE
		)

		self.tree.add_popup_menu_option('-', item=self.treenode)

		self.tree.add_popup_menu_option(
			label='Remove', 
			function_action=self.__remove_video_changed_event, 
			item=self.treenode, icon=conf.ANNOTATOR_ICON_DELETE
		)

	def choose_file(self): self._file.click()
	def create_object(self): return Object2D(self)
	def create_image(self): return Image(self)
	def create_geometry(self): return Geometry(self)
	def create_note(self): return Note(self)



	#####################################################################################
	########### EVENTS ##################################################################
	#####################################################################################
	def __capture_current_frame(self):
		image = self.create_image()

		current_index = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
		current_index = int(current_index if current_index==0 else (current_index-1))
		self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_index )

		image.name = "frame({0})".format(current_index)

		res, img = self.video_capture.read()
		image.image = img

	def __remove_video_changed_event(self): 
		project = self.project
		project -= self
		if len(project.videos)==0: self.close()

	def __file_changed_event(self):
		self.filepath = self._file.value
	
	#####################################################################################
	########### PROPERTIES ##############################################################
	#####################################################################################

	
	@property
	def mainwindow(self): 	return self.project.mainwindow

	@property
	def tree(self): return self._project.tree

	@property
	def filepath(self): return self._file.value
	@filepath.setter 
	def filepath(self, value):
		Video.filepath.fset(self, value)		
		self.mainwindow.video 	= self.video_capture
		self._file.value 		= value

		fps 	= self.video_capture.get(cv2.CAP_PROP_FPS)
		width 	= self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
		height 	= self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

		self._fps_label.value = "FPS: {0}".format(fps)
		self._width_label.value = "Width: {0}".format(width)
		self._height_label.value = "Height: {0}".format(height)
		
	