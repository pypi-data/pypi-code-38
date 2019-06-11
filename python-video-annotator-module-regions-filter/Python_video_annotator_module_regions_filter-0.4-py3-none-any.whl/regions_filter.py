import sys, os, shutil, re, pyforms, numpy as np, cv2
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls 	 import ControlFile
from pyforms.controls 	 import ControlPlayer
from pyforms.controls 	 import ControlButton
from pyforms.controls 	 import ControlNumber
from pyforms.controls 	 import ControlSlider
from pyforms.controls 	 import ControlCheckBox
from pyforms.controls 	 import ControlText
from pyforms.controls 	 import ControlCheckBoxList
from pyforms.controls 	 import ControlProgress
from pyforms.controls 	 import ControlList
from pyforms.controls 	 import ControlCombo
from pyforms.controls 	 import ControlEmptyWidget

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog



from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models.models.video.objects.object2d import Object2D

from pythonvideoannotator_models_gui.models.video.objects.geometry import Geometry

from pythonvideoannotator_models_gui.dialogs import ObjectsDialog
from geometry_designer.modules.geometry_manual_designer.GeometryManualDesigner import GeometryManualDesigner


class RegionsFilter(BaseWidget):

	def __init__(self, parent=None):
		BaseWidget.__init__(self, 'Regions filter', parent_win=parent)
		self.mainwindow = parent

		self.set_margin(5)
		
		self.setMinimumHeight(300)
		self.setMinimumWidth(500)

		self._paths = []

		self._pathspanel	= ControlEmptyWidget('Path to process')
		self._geomspanel 	= ControlEmptyWidget('Geometries')		
		self._apply  		= ControlButton('Apply', checkable=True)
		self._progress  	= ControlProgress('Progress')

		
		self._formset = [
			'_pathspanel',
			'_geomspanel',
			'_apply',
			'_progress'
		]

		self.load_order = ['_start', '_end', '_panel']

		self.paths_dialog = DatasetsDialog(self)
		self.paths_dialog.objects_filter  = lambda x: isinstance(x, Object2D)
		self.paths_dialog.datasets_filter = lambda x: isinstance(x, (Contours,Path) )
		self._pathspanel.value = self.paths_dialog

		self.geoms_dialog = ObjectsDialog(self)
		self.geoms_dialog.objects_filter = lambda x: isinstance(x, Geometry)
		self._geomspanel.value = self.geoms_dialog


	
		self._apply.value = self.__apply_btn_event
		self._apply.icon  = conf.ANNOTATOR_ICON_REGIONS

		self._progress.hide()

	def __reload_tracks_event(self):
		self._tracks.clearItems()
		for track in self.mainwindow._time.tracks:
			self._tracks.addItem(str(track.title), track)
	
	def __apply_btn_event(self):

		if self._apply.checked:
			self._pathspanel.enabled	= False
			self._geomspanel.enabled 	= False
			self._apply.label 			= 'Cancel'

			# calculate the total number of frames to analyse
			total_2_analyse  = 0
			for video, (begin, end), datasets_list in self.paths_dialog.selected_data:
				total_2_analyse += end-begin+1

			self._progress.min = 0
			self._progress.max = total_2_analyse
			self._progress.show()

			contours = []
			for video, geometries in self.geoms_dialog.selected_data:
				for geometry_object in geometries:
					for contour in geometry_object.geometry:
						contours.append(np.int32(contour[1]))

			count = 0
			for video, (begin, end), datasets_list in self.paths_dialog.selected_data:
				begin, end = int(begin), int(end)+1

				for path_dataset in datasets_list:
					object2d  = path_dataset.object2d
					value_obj = object2d.create_value()
					value_obj.name = 'regions-filter ({0})'.format(len(object2d))
					for index in range(begin, end+1):
						pt = path_dataset.get_position(index)
						for contour in contours:
							dist = cv2.pointPolygonTest(contour, pt, True)
							value_obj.set_value(index, dist)
						count += 1
						self._progress.value = count

			self._pathspanel.enabled	= True
			self._geomspanel.enabled 	= True
			self._apply.label 			= 'Apply'
			self._progress.hide()

	
	def add_event_2_timeline(self, track, evt_name, begin, end):
		self.mainwindow.add_event_2_timeline(track, evt_name, begin, end)
	

	def add_dataset_event(self, dataset):
		if isinstance(dataset, Path): self._paths += [dataset, True]

	def removed_dataset_event(self, dataset):
		if isinstance(dataset, Path): self._paths -= dataset

	def removed_object_event(self, obj):
		items2remove = []
		for i, (item, checked) in enumerate(self._paths.items):
			if item.object2d==obj: items2remove.append(i)
		for i in sorted(items2remove,reverse=True): self._paths -= i


	###########################################################################
	### PROPERTIES ############################################################
	###########################################################################

	@property
	def video_filename(self): return None
	@video_filename.setter
	def video_filename(self, value): 
		self._panel.value.video_filename = value
		self._start.max 	= self._panel.value.total_n_frames
		self._end.max 		= self._panel.value.total_n_frames
		

	@property
	def paths(self): return self._paths.value
	@paths.setter
	def paths(self, value):  self._paths.value = value

	def save(self, data): return data
	def load(self, data): pass

	

if __name__ == "__main__": pyforms.startApp(RegionsFilter)