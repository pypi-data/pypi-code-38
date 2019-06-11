import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlBoundingSlider
from pyforms.controls import ControlEmptyWidget
from pythonvideoannotator_models_gui.dialogs.videos.videos_selector import VideosSelectorDialog

class VideosDialog(BaseWidget):

	def __init__(self, parent_win=None):
		BaseWidget.__init__(self, 'Videos and intervals selector', parent_win=parent_win)

		self._panel  	= ControlEmptyWidget(default=VideosSelectorDialog(parent_win=self))
		self._interval 	= ControlBoundingSlider('Interval', horizontal=True)
		
		self.formset = [
			'_panel', 
			'_interval'
		]

		self._intervals = {}

		self._panel.value.video_selection_changed_event = self.__video_selection_changed_event
		self._interval.changed_event = self.__update_intervals_event

	#####################################################################
	### PRIVATE FUNCTIONS ###############################################
	#####################################################################

	def __update_intervals_event(self):
		self._intervals[self.selected_video] = self._interval.value

	def __video_selection_changed_event(self):
		video = self.selected_video
		
		if video is not None and video.video_capture is not None:
			self._interval.max 	 = video.video_capture.get(7)
			if video not in self._intervals.keys(): 
				self._intervals[video] = 0, self._interval.max
			
			self._interval.value = self._intervals[video]
		self.video_selection_changed_event()

	#####################################################################
	### EVENTS ##########################################################
	#####################################################################

	def video_selection_changed_event(self):  pass

	def destroy(self, destroyWindow = True, destroySubWindows = True):
		self._panel.value.destroy(destroyWindow, destroySubWindows)
		super(VideosDialog, self).destroy(destroyWindow, destroySubWindows)
	

	#####################################################################
	### FUNCTIONS #######################################################
	#####################################################################

	def refresh(self):  self._panel.value.refresh()
	def clear(self):  self._panel.value.clear()
	def __add__(self, other): self._panel.value += other; return self
	def __sub__(self, other): self._panel.value -= other; return self

	#####################################################################
	### PROPERTIES ######################################################
	#####################################################################

	@property
	def selected_video(self): 		return self._panel.value.selected_video
	
	@property
	def videos(self): return self._panel.value.videos

	@property
	def interval_visible(self): return self._interval.visible
	@interval_visible.setter
	def interval_visible(self, value):
		if value:
			self._interval.show()
		else:
			self._interval.hide()
	

	@property
	def selected_data(self):
		for video in self._panel.value.selected_data:
			begin, end =  self._intervals.get(video, (0, video.total_frames)  )
			yield video, (begin, end )

	


if __name__ == "__main__":	 pyforms.startApp( VideosDialog )