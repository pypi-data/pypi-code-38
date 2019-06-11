import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlCheckBoxList
from pythonvideoannotator_models.models.video import Video
from pythonvideoannotator_models.models.video.objects.image import Image
from pythonvideoannotator_models_gui.dialogs.dialog import Dialog
from pythonvideoannotator_models.models.video.objects.object2d import Object2D
from pythonvideoannotator_models.models.video.objects.object2d.datasets.path import Path

class ImagesDialog(Dialog,BaseWidget):

	def __init__(self, parent_win=None):
		BaseWidget.__init__(self, 'Images selector', parent_win=parent_win)
		
		self._videos = ControlCheckBoxList('Videos filter')
		self._images = ControlCheckBoxList('Images filter')

		Dialog.__init__(self)
		

		self.formset = [('_videos','||','_images')]
		self._videos.selection_changed_event 	= self.__selection_changed_event
		self._videos.changed_event  			= self.__update_images

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
	def refresh(self):
		self._videos.refresh()
		self._images.refresh()
	
	def __add__(self, other):
		if isinstance(other, Video): self._videos += (other, False)
		if isinstance(other, Image): self.__update_images()
		return self

	def __sub__(self, other):
		if isinstance(other, Video): 	
			self._videos -= other
			self.__update_images()
		if isinstance(other, Image): self.__update_images()
		return self
	
	
	def __update_images(self):
		"""
		Update the objects in the list
		"""
		images = [elem for elem, checked in self._images.items]

		images_list = []
		for video, checked in self._videos.items:
			for img in video.images:
				images_list.append(img)
				if not checked and img in images:
					self._images -= img
				elif checked and img not in images:
					self._images += (img, False)
				
		for img in images:
			if img not in images_list: self._images -= img


	#####################################################################
	### PROPERTIES ######################################################
	#####################################################################

	@property
	def single_select(self): return self._images.value
	@single_select.setter
	def single_select(self, value): return self._images.value

	@property
	def images(self): return self._images.value

	@property
	def selected_data(self):
		videos 	= self._videos.value
		images 	= self._images.value
		res 	= []
		for video in videos:
			images_list = []
			for img in video.images: 
				images_list.append(img)
			res.append( (video, images_list) )
		return res
		
	@property
	def selected_video(self): 
		###########################################
		# current mouse selected video
		###########################################
		index = self._videos.selected_row_index
		if index<0: return None

		video, selected = self._videos.items[index]
		return video

	
	
if __name__ == "__main__":	 pyforms.startApp( ImagesDialog )