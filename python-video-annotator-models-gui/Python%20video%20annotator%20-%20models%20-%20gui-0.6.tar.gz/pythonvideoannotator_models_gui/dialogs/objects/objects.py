import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlCheckBoxList
from pythonvideoannotator_models.models.video import Video
from pythonvideoannotator_models.models.video.objects.video_object import VideoObject
from pythonvideoannotator_models_gui.dialogs.dialog import Dialog
from pythonvideoannotator_models.models.video.objects.object2d import Object2D
from pythonvideoannotator_models.models.video.objects.object2d.datasets.path import Path

class ObjectsDialog(Dialog,BaseWidget):

	def __init__(self, parent_win=None, title='Objects selector'):
		BaseWidget.__init__(self, title, parent_win=parent_win)
		
		self._objects_filter = None
		
		self._videos  = ControlCheckBoxList('Videos filter')
		self._objects = ControlCheckBoxList('Objects filter')

		self._videos.add_popup_menu_option('Select video', self.__selection_changed_event)

		Dialog.__init__(self)
		

		self.formset  = [('_videos','||','_objects')]
		self._videos.selection_changed_event 	= self.__selection_changed_event
		self._videos.changed_event  			= self.update_objects
		self._objects.changed_event 			= self.__objects_changed_event


	#####################################################################
	### PRIVATE FUNCTIONS ###############################################
	#####################################################################

	def __selection_changed_event(self): self.video_selection_changed_event()

	def __objects_changed_event(self): self.objects_changed_event()

	#####################################################################
	### EVENTS ##########################################################
	#####################################################################

	def video_selection_changed_event(self): pass
	def objects_changed_event(self): pass

	#####################################################################
	### FUNCTIONS #######################################################
	#####################################################################

	# used to update automaticly the name of the videos, objects and paths
	def refresh(self):
		self._videos.refresh()
		self._objects.refresh()
	
	def __add__(self, other):
		if isinstance(other, Video): self._videos += (other, False)
		if isinstance(other, VideoObject): self.update_objects()
		return self

	def __sub__(self, other):
		if isinstance(other, Video): 	
			self._videos -= other
			self.update_objects()
		if isinstance(other, VideoObject): self.update_objects()
		return self
	
	
	def update_objects(self):
		"""
		Update the objects in the list
		"""
		objects = [elem for elem, checked in self._objects.items]

		objects_list = []
		for video, checked in self._videos.items:
			for obj in video.objects:
				if self._objects_filter and not self._objects_filter(obj): continue
				
				objects_list.append(obj)
				if not checked and obj in objects:
					self._objects -= obj
				elif checked and obj not in objects:
					self._objects += (obj, False)

		for obj in objects:
			if obj not in objects_list: self._objects -= obj


	#####################################################################
	### PROPERTIES ######################################################
	#####################################################################

	@property
	def objects(self): return self._objects.value

	@property
	def selected_video(self): 
		###########################################
		# current mouse selected video
		###########################################
		index = self._videos.selected_row_index
		if index<0: return None

		video, selected = self._videos.items[index]
		return video

	

	@property
	def selected_data(self):
		videos 	= self._videos.value
		objects = self._objects.value
		res 	= []
		for video in videos:
			objects_list = []
			for obj in video.objects: 
				if obj in objects: objects_list.append(obj)
			res.append( (video, objects_list) )
		return res

	@property
	def objects_filter(self): return self._objects_filter
	@objects_filter.setter
	def objects_filter(self, value): self._objects_filter = value
		
	
	
if __name__ == "__main__":	 pyforms.startApp( ObjectsDialog )