import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlCheckBoxList
from pythonvideoannotator_models.models.video import Video
from pythonvideoannotator_models_gui.dialogs.dialog import Dialog

class VideosSelectorDialog(Dialog, BaseWidget):

	def __init__(self, parent_win=None):
		BaseWidget.__init__(self, 'Videos selector', parent_win=parent_win)
		self._videos  = ControlCheckBoxList('Videos filter')

		Dialog.__init__(self)
		
		
		self.formset = ['_videos']
		self._videos.selection_changed_event 	= self.__selection_changed_event	
		
		#for video in conf.PROJECT.videos: self += video

		
		
	#####################################################################
	### PRIVATE FUNCTIONS ###############################################
	#####################################################################

	def __selection_changed_event(self): self.video_selection_changed_event()

	#####################################################################
	### EVENTS ##########################################################
	#####################################################################

	def video_selection_changed_event(self): pass

	#####################################################################
	### FUNCTIONS #######################################################
	#####################################################################

	# used to update automaticly the name of the videos, objects and paths
	def refresh(self): self._videos.refresh()
	def clear(self): self._videos.clear()
	
	def __add__(self, other):
		if isinstance(other, Video): self._videos += (other, False)
		return self

	def __sub__(self, other):
		if isinstance(other, Video): self._videos -= other
		return self
	
	
	

	#####################################################################
	### PROPERTIES ######################################################
	#####################################################################

	@property
	def selected_data(self): return self._videos.value
		
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
	def videos(self): return self._videos.value
	
	
	
if __name__ == "__main__":	 pyforms.startApp( VideosSelectorDialog )