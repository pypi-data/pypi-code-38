import pyforms
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlSlider
from pyforms.controls import ControlButton
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlProgress
from pyforms.controls import ControlImage

from pythonvideoannotator_models_gui.models.video.objects.object2d.utils import points as pts_utils
from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours

import numpy as np, cv2
from confapp import conf




class DistancesWindow(BaseWidget):

	def __init__(self, parent=None):
		super(DistancesWindow, self).__init__('Distances', parent_win=parent)
		self.mainwindow = parent

		self.set_margin(5)
        

		#self.layout().setMargin(5)
		self.setMinimumHeight(400)
		self.setMinimumWidth(800)

		self._datasets_panel= ControlEmptyWidget('Paths')
		self._progress  	= ControlProgress('Progress')		
		self._apply 		= ControlButton('Apply', checkable=True)
			
		self._formset = [
			'_datasets_panel',
			'_apply',
			'_progress'
		]

		self.load_order = ['_datasets_panel']

		self.datasets_dialog 		= DatasetsDialog(self)
		self._datasets_panel.value = self.datasets_dialog
		self.datasets_dialog.datasets_filter = lambda x: isinstance(x, (Path, Contours))

		self._apply.value		= self.__apply_event
		self._apply.icon 		= conf.ANNOTATOR_ICON_PATH

		self._progress.hide()



	###########################################################################
	### EVENTS ################################################################
	###########################################################################



	###########################################################################
	### PROPERTIES ############################################################
	###########################################################################

	@property
	def datasets(self): return self.datasets_dialog.datasets
	

	def __apply_event(self):

		if self._apply.checked:
			
			self._datasets_panel.enabled = False			
			self._apply.label 			= 'Cancel'

			total_2_analyse  = 0
			for video, (begin, end), datasets in self.datasets_dialog.selected_data:
				total_2_analyse += (end-begin+1)*len(datasets)*len(datasets)

			self._progress.min = 0
			self._progress.max = total_2_analyse
			self._progress.show()

			count = 0
			for video, (begin, end), datasets in self.datasets_dialog.selected_data:
				begin 	= int(begin)
				end 	= int(end)+1

				if len(datasets)<2: continue

				for d1_index in range(len(datasets)):
					for d2_index in range(len(datasets)):
						if d1_index==d2_index: break
						if not self._apply.checked: break

						set1 = datasets[d1_index]
						set2 = datasets[d2_index]

						val = set1.object2d.create_value()
						val.name = "distance-between ({0}) and ({1})".format(set1.name, set2.name)

						for index in range(begin, end):	
							if not self._apply.checked: break

							pos1 = set1.get_position(index)
							if pos1 is None: continue
							pos2 = set2.get_position(index)
							if pos2 is None: continue

							dist = pts_utils.lin_dist(pos1, pos2)
							val.set_value(index, dist)

							self._progress.value = count
							count += 1

						count = d1_index*d2_index*(end-begin+1)

			self._datasets_panel.enabled = True	
			self._apply.label 			= 'Apply'
			self._apply.checked 		= False
			self._progress.hide()





	


if __name__ == '__main__': 
	pyforms.startApp(DistancesWindow)
