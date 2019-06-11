import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlBoundingSlider
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlButton
from pythonvideoannotator_models_gui.dialogs.datasets.datasets_selector import DatasetsSelectorDialog

class DatasetsDialog(BaseWidget):


	def __init__(self, parent_win=None):
		BaseWidget.__init__(self, 'Datasets', parent_win=parent_win)


		self._panel  	= ControlEmptyWidget(default=DatasetsSelectorDialog(parent_win=self))
		self._interval 	= ControlBoundingSlider('Interval', horizontal=True)
		self._apply_btn = ControlButton('Apply')
		
		self.formset = [
			'_panel', 
			'_interval',
			'_apply_btn',
		]

		self._intervals = {}

		self._panel.value.video_selection_changed_event = self.__video_selection_changed_event
		self._interval.changed_event = self.__update_intervals_event
		self._apply_btn.hide()

	#####################################################################
	### PRIVATE FUNCTIONS ###############################################
	#####################################################################

	def __update_intervals_event(self):
		self._intervals[self.selected_video] = self._interval.value

	def __video_selection_changed_event(self):
		video = self.selected_video
		
		if video is not None and video.video_capture is not None:
			self._interval.max = video.video_capture.get(7)
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
		super(DatasetsDialog, self).destroy(destroyWindow, destroySubWindows)
	

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
	def videos(self): 		return self._panel.value.videos
	
	@property
	def datasets(self): 		return self._panel.value.datasets

	@property
	def datasets_changed_event(self): return self._panel.value.datasets_changed_event
	@datasets_changed_event.setter
	def datasets_changed_event(self, value): self._panel.value.datasets_changed_event = value
	

	@property
	def objects_changed_event(self): return self._panel.value.objects_changed_event
	@objects_changed_event.setter
	def objects_changed_event(self, value): self._panel.value.objects_changed_event = value
	
	
	
	@property
	def selected_video(self): 		return self._panel.value.selected_video

	@property
	def selected_video_range(self): return self._intervals.value

	
	@property
	def selected_data(self):
		for video, paths in self._panel.value.selected_data:
			begin, end =  self._intervals.get(video, (0, video.video_capture.get(7))  )
			yield video, (begin, end ), paths

	@property
	def apply_event(self): 				return self._apply_btn.value
	@apply_event.setter
	def apply_event(self, value): 		
		if value is not None: self._apply_btn.show()
		self._apply_btn.value = value

	@property
	def interval_visible(self): return self._interval.visible
	@interval_visible.setter
	def interval_visible(self, value): 
		if value:
			self._interval.show()
		else:
			self._interval.hide()
			
	@property
	def objects_filter(self): return self._panel.value.objects_filter
	@objects_filter.setter
	def objects_filter(self, value): self._panel.value.objects_filter = value

	@property
	def datasets_filter(self): return self._panel.value.datasets_filter
	@datasets_filter.setter
	def datasets_filter(self, value): self._panel.value.datasets_filter = value





if __name__ == "__main__":	 pyforms.start_app( DatasetsDialog )