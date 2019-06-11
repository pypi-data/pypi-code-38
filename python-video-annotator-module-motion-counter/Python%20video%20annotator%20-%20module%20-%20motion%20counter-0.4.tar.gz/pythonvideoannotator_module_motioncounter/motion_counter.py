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
from pyforms.controls 	 import ControlEmptyWidget
from pyforms.controls 	 import ControlProgress
from pyforms.controls 	 import ControlCombo

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.dialogs import ObjectsDialog

from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models_gui.models.video.objects.image import Image

class MotionCounter(BaseWidget):

	def __init__(self, parent=None):
		BaseWidget.__init__(self, 'Motion counter', parent_win=parent)

		self.set_margin(5)
		
		self.setMinimumHeight(300)
		self.setMinimumWidth(500)

		self._player	= ControlPlayer('Player')
		self._datasets 	= ControlEmptyWidget('Paths', 			default=DatasetsDialog() )
		self._backgrounds = ControlEmptyWidget('Backgrounds', 	default=ObjectsDialog()  )
		self._show_diff	= ControlCheckBox('Show diffs boxes')
		self._threshold	= ControlSlider('Threshold', default=5,  minimum=1, maximum=255)
		self._radius	= ControlSlider('Radius', default=30,  minimum=1, maximum=200)
		self._apply  	= ControlButton('Apply', checkable=True)
		self._compare  	= ControlCombo('Compare with')
		self._progress 	= ControlProgress('Progress')

		
		self._formset = [
			'_datasets',
			'=',
			'_compare',
			'_backgrounds',
			('_threshold', '_radius', '_show_diff'),
			'_player',
			'_apply',
			'_progress'
		]

		self._compare.add_item('Last frame', 1)
		self._compare.add_item('First frame', 2)
		self._compare.add_item('Background image', 3)

		self.load_order = ['_threshold', '_radius', '_show_diff']

		self._backgrounds.value.datasets_filter   			= lambda x: isinstance(x, Image )
		self._datasets.value.datasets_filter   				= lambda x: isinstance(x, (Contours, Path) )
		self._player.process_frame_event 					= self.__process_frame_event
		self._datasets.value.video_selection_changed_event 	= self.__video_selection_changed_event
		
		self._compare.changed_event = self.__compare_changed_event

		self._apply.value 		= self.__apply_btn_event
		self._apply.icon 		= conf.ANNOTATOR_ICON_MOTION
		
		self._progress.hide()
		self._backgrounds.hide()

	###########################################################################
	### EVENTS ################################################################
	###########################################################################

	def __compare_changed_event(self):
		if self._compare.value==1:
			self._backgrounds.hide()

		elif self._compare.value==2:
			self._backgrounds.hide()

		elif self._compare.value==3:
			self._backgrounds.show()

		self._lastframe = None
		


	def __video_selection_changed_event(self):
		video = self._datasets.value.selected_video
		if video is not None: self._player.value = video.video_capture

	def __process_frame_event(self, frame):
		index 			= self._player.video_index-1
		selected_video 	= self._datasets.value.selected_video
		radius 			= self._radius.value
		threshold 		= self._threshold.value

		show_diff 		= self._show_diff.value

		compare_with = self._compare.value
		if compare_with==3 and len(self._backgrounds.value.objects):
			background_img = self._backgrounds.value.objects[0].image
			background_img = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)
		else:
			background_img  = None

		for video, (begin, end), datasets in self._datasets.value.selected_data:
			if video != selected_video: continue

			for dataset in datasets:
				pos = dataset.get_position(index)
				if pos is None: continue

				if show_diff:
					# calculate the cut
					x,y	  = pos
					cutx  = int(round(x-radius))
					cuty  = int(round(y-radius))
					cutxx = int(round(x+radius))
					cutyy = int(round(y+radius))
					if cutx<0: 
						cutx=0
					if cutxx>frame.shape[1]: 
						cutxx = frame.shape[1]
					if cuty<0: 
						cuty=0
					if cutyy>frame.shape[0]: 
						cutyy = frame.shape[0]

					gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

					small 		 = gray[cuty:cutyy, cutx:cutxx].copy()

					circular_mask = np.zeros( (cutyy-cuty, cutxx-cutx), dtype=np.uint8 )
					cv2.circle(circular_mask, (cutyy-cuty, cutxx-cutx), radius, 255, -1 )

					small_masked = cv2.bitwise_and(circular_mask, small)
					
					if not hasattr(self, '_lastframe') or type(self._lastframe) is not np.ndarray:
						if self._compare.value==1 or self._compare.value==2:
							self._lastframe = gray							
						elif self._compare.value==3:
							self._lastframe = background_img
						
					if type(self._lastframe) is np.ndarray:
						last_masked = cv2.bitwise_and(circular_mask, self._lastframe[cuty:cutyy, cutx:cutxx])	

						diff = cv2.absdiff(small_masked, last_masked)

						cv2.circle(frame, pos, radius, (0,0,0), -1)

						frame[cuty:cutyy, cutx:cutxx] += cv2.merge( (diff, diff, diff) )

					if self._compare.value==1: self._lastframe = gray
				else:
					cv2.circle(frame, pos, radius, (0,0,255), 2)
		return frame
			
	def __apply_btn_event(self):

		if self._apply.checked:
			self._datasets.enabled 	= False
			self._show_diff.enabled = False
			self._threshold.enabled = False
			self._player.enabled 	= False
			self._radius.enabled 	= False
			self._player.stop()
			self._apply.label 		= 'Cancel'

			total_2_analyse  = 0
			for video, (begin, end), datasets in self._datasets.value.selected_data:
				total_2_analyse += end-begin+1

			self._progress.min = 0
			self._progress.max = total_2_analyse
			self._progress.show()

			radius    = self._radius.value
			threshold = self._threshold.value

			count = 0
			for video, (begin, end), datasets in self._datasets.value.selected_data:
				begin = int(begin)
				end = int(end)+1

				capture = cv2.VideoCapture(video.filepath)
				capture.set(cv2.CAP_PROP_POS_FRAMES, begin)

				last_image = [None for x in datasets]

				compare_with = self._compare.value
				if compare_with==3:
					if len(self._backgrounds.value.objects):
						background_img = self._backgrounds.value.objects[0].image
						background_img = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)
					else:
						self.critical('No background selected')
						break
				else:
					background_img  = None


				for index in range(begin, end):
					res, frame = capture.read()
					if not res: break
					if not self._apply.checked: break

					for dataset_index, dataset in enumerate(datasets):
						pos = dataset.get_position(index)
						if pos is None: continue

						x,y	  = pos
						cutx  = int(round(x-radius))
						cuty  = int(round(y-radius))
						cutxx = int(round(x+radius))
						cutyy = int(round(y+radius))
						if cutx<0: 
							cutx=0
						if cutxx>frame.shape[1]: 
							cutxx = frame.shape[1]
						if cuty<0: 
							cuty=0
						if cutyy>frame.shape[0]: 
							cutyy = frame.shape[0]

						gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

						small 		 = gray[cuty:cutyy, cutx:cutxx].copy()

						circular_mask = np.zeros( (cutyy-cuty, cutxx-cutx), dtype=np.uint8 )
						cv2.circle(circular_mask, (cutyy-cuty, cutxx-cutx), radius, 255, -1 )

						small_masked = cv2.bitwise_and(small, small, circular_mask)

						if type(last_image[dataset_index]) is not np.ndarray: 
							last_image[dataset_index]  	  = small_masked
							if compare_with==1 or compare_with==2:
								last_image[dataset_index] = gray
							elif compare_with==3:
								last_image[dataset_index] = background_img

						segment 	= last_image[dataset_index]
						last_masked = cv2.bitwise_and(circular_mask, segment[cuty:cutyy, cutx:cutxx] )	

						diff = cv2.absdiff(small_masked, last_masked)
						diff[diff< threshold]  = 0
						diff[diff>=threshold] = 1

						motion = np.sum(diff)
						dataset.set_motion(index, motion)

						if compare_with==1: 
							last_image[dataset_index] = gray

					self._progress.value = count
					count += 1
		
			self._datasets.enabled 	= True
			self._show_diff.enabled = True
			self._threshold.enabled = True
			self._player.enabled 	= True
			self._radius.enabled 	= True
			self._apply.label 		= 'Apply'
			self._apply.checked 	= False
			self._progress.hide()


	

	




	

if __name__ == "__main__": pyforms.start_app(MotionCounter)