import pyforms
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlSlider
from pyforms.controls import ControlButton
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlProgress

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.value import Value

import numpy as np
from pythonvideoannotator_models.utils.tools import savitzky_golay
from confapp import conf






class SmoothPathsWindow(BaseWidget):

	def __init__(self, parent=None):
		super(SmoothPathsWindow, self).__init__('Smooth paths', parent_win=parent)
		self.mainwindow = parent

		self.set_margin(5)
		self.setMinimumHeight(400)
		self.setMinimumWidth(800)



		self._datasets_panel= ControlEmptyWidget('Paths')
		self._progress      = ControlProgress('Progress')       
		self._apply         = ControlButton('Apply', checkable=True)

		self._winsize   = ControlSlider('Window size', minimum=3, default=3, maximum=100)
		self._order     = ControlSlider('Order', minimum=0, default=0, maximum=10)
		self._deriv     = ControlSlider('Derivative', minimum=0, default=0, maximum=10)
		self._rate      = ControlSlider('Rate', minimum=0, default=0, maximum=10)

			
		self._formset = [
			'_datasets_panel',
			'=',
			'_winsize',
			'_order',
			'_deriv',
			'_rate', 
			' ',
			'_apply',
			'_progress'
		]

		self.load_order = ['_datasets_panel']

		self.datasets_dialog        = DatasetsDialog(self)
		self._datasets_panel.value = self.datasets_dialog
		self.datasets_dialog.datasets_filter = lambda x: isinstance(x, (Path, Value))

		self._apply.value       = self.__apply_event
		self._apply.icon        = conf.ANNOTATOR_ICON_PATH

		self._progress.hide()

	def init_form(self):
		super(SmoothPathsWindow, self). init_form()
		self.datasets_dialog.project = self.mainwindow.project

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

			if self._winsize.value<self._order.value+2:
				self.message('The Window size has to be bigger than the Order + 2 ', 'Error', 'error')
				self._apply.checked=False
				return

			if self._order.value<self._deriv.value:
				self.message('The Derivative has to be less than or equal to the Order', 'Error', 'error')
				self._apply.checked=False
				return

			if len(self.datasets_dialog.datasets)==0:
				self.message('You have to select at least one dataset', 'Error', 'error')
				self._apply.checked=False
				return
			
			self._datasets_panel.enabled    = False         
			self._apply.label           = 'Cancel'

			total_2_analyse  = 0
			for video, (begin, end), datasets in self.datasets_dialog.selected_data:
				total_2_analyse += (end-begin+1)*2

			self._progress.min = 0
			self._progress.max = total_2_analyse
			self._progress.show()

			count = 0
			for video, (begin, end), datasets in self.datasets_dialog.selected_data:
				begin   = int(begin)
				end     = int(end)+1

				for dataset in datasets:
					if isinstance(dataset, Path):
						values = [dataset.get_position(index) for index in range(begin, end)]
					elif isinstance(dataset, Value):
						values = [dataset.get_value(index) for index in range(begin, end)]

					#remove the None positions
					for curr_idx in range(len(values)):
						if values[curr_idx] is None:

							#Search for a not None position on the past
							new_vals = None
							for prev_idx in range(curr_idx, 0, -1):
								new_vals = values[prev_idx]
								if new_vals is not None: break

							#Search for a not None position on the future
							if new_vals is None:
								for nex_idx in range(curr_idx, end):
									new_vals = values[nex_idx]
									if new_vals is not None: break

							#No positions were found, assume 0,0 position
							if new_vals is None:
								if isinstance(dataset, Path):
									new_vals = (0,0)
								elif isinstance(dataset, Value):
									new_vals = 0

							values[curr_idx]=new_vals
						
						self._progress.value = count
						count += 1

					winsize = self._winsize.value
					winsize = winsize+1 if (winsize % 2)==0 else winsize

					if isinstance(dataset, Path):
						xs = np.array([x for x, y in values])
						ys = np.array([y for x, y in values])
						xs = savitzky_golay(xs, winsize, self._order.value, self._deriv.value, self._rate.value)
						ys = savitzky_golay(ys, winsize, self._order.value, self._deriv.value, self._rate.value)
						for index in range(begin, end):
							pos = dataset.get_position(index)
							if pos is not None:
								dataset.set_position(index, xs[index], ys[index])                       
							self._progress.value = count
							count += 1
					elif isinstance(dataset, Value):
						xs = np.array(values)
						xs = savitzky_golay(xs, winsize, self._order.value, self._deriv.value, self._rate.value)
						for index in range(begin, end):
							val = dataset.get_value(index)
							if val is not None:
								dataset.set_value(index, xs[index])                     
							self._progress.value = count
							count += 1
					
					
					

				

			self._datasets_panel.enabled    = True  
			self._apply.label           = 'Apply'
			self._apply.checked         = False
			self._progress.hide()





	


if __name__ == '__main__': 
	pyforms.startApp(SmoothPathsWindow)
