import pyforms, math, os

from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlToolBox
from pyforms.controls import ControlSlider
from pyforms.controls import ControlPlayer
from pyforms.controls import ControlDir
from pyforms.controls import ControlText
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlCheckBoxList
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlProgress

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.dialogs import ImagesDialog

from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path 	 import Path
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.value 	 import Value

from pythonvideoannotator_module_virtualobjectgenerator.videosexporter.videosexporter_preview import VideosExporterPreview
from pythonvideoannotator_module_virtualobjectgenerator.videosexporter.videosexporter_process import VideosExporterProcess

class VideosExporterGui(BaseWidget, VideosExporterPreview, VideosExporterProcess):

	def __init__(self, parent=None):
		super(VideosExporterGui, self).__init__('Videos exporter', parent_win=parent)
		
		self.set_margin(5)
		self.setMinimumHeight(400)
		self.setMinimumWidth(400)

		self._toolbox 		= ControlToolBox('Tool')

		self._panel_area	= ControlEmptyWidget('Set the object area', 	 default=DatasetsDialog(self))
		self._panel_colors  = ControlEmptyWidget('Set the object color', 	 default=DatasetsDialog(self))
		self._panel_imgs	= ControlEmptyWidget('Set the video background', default=ImagesDialog(self)  )
		
		#### path panel ################################################
		self._panel_path	= ControlEmptyWidget('Set the object path',  default=DatasetsDialog(self) )
		self._drawpath 		= ControlCheckBox('Draw paths')
		################################################################

		#### draw events ###############################################
		self._drawevents	= ControlCheckBoxList('Events')
		self._eventstitles  = ControlCheckBox('Draw titles')
		self._evtsreload1   = ControlButton('Reload events')
		################################################################

		#### split by events ###########################################
		self._splitevents	= ControlCheckBoxList('Events')
		self._evtsreload2   = ControlButton('Reload events')
		################################################################


		self._codec 		= ControlCheckBox('Force AVI')
		self._outdir 		= ControlDir('Output directory')
		self._outfile 		= ControlText('Output file name')
		
		self._player 		= ControlPlayer('Player')
		self._progress  	= ControlProgress('Progress')
		self._apply 		= ControlButton('Export video(s)', checkable=True)
		self._apply.icon 	= conf.ANNOTATOR_ICON_PATH
		self._apply.enabled = False
		
		self._usefixedsize  = ControlCheckBox('Use a fixed size')
		self._usefixedcolor = ControlCheckBox('Use a fixed color')
		self._radius		= ControlSlider('Circle radius', default=10,  minimum=1, maximum=300)
		self._color			= ControlText('BGR color', default='255,255,255')
		
		self.formset = [			
			('_toolbox','||','_player'),
			'=',
			'_outdir',
			('_outfile','_codec'),
			'_apply',
			'_progress'
		]

		self._toolbox.value = [
			('Path', 						[self._panel_path,  self._drawpath]), 
			('Circle (optional)', 			[self._panel_area,  (self._usefixedsize, self._radius)]),
			('Circle color (optional)', 	[self._panel_colors,(self._usefixedcolor, self._color)]),
			('Background (optional)',		[self._panel_imgs]),
			('Draw events (optional)',		[self._evtsreload1, self._drawevents, self._eventstitles]),
			('Split files by events (optional)', [self._evtsreload2, self._splitevents]),			
		]


		self._panel_path.value.datasets_filter   = lambda x: isinstance(x, (Contours, Path) )
		#self._panel_area.value.datasets_filter   = lambda x: isinstance(x, Value )
		self._panel_colors.value.datasets_filter = lambda x: isinstance(x, (Contours, Path) ) and hasattr(x, 'has_colors_avg') and x.has_colors_avg

		### Set the controls events #############################################
		self._evtsreload1.value 		    				 = self.__reload_events
		self._evtsreload2.value 		    				 = self.__reload_events
		self._outfile.changed_event 						 = self.outputfile_changed_event
		self._usefixedsize.changed_event 					 = self.__usefixedsize_changed_event
		self._usefixedcolor.changed_event 					 = self.__usefixedcolor_changed_event
		self._splitevents.selection_changed_event 			 = self.outputfile_changed_event
		self._panel_path.value.video_selection_changed_event = self.__video_selection_changed_event
		self._codec.changed_event 							 = self.__video_selection_changed_event
		## function from VideosExporterProcess class
		self._apply.value				 					 = self.apply_event 			
		## function from VideosExporterPreview class
		self._player.process_frame_event 					 = self.player_processframe_event
				
		self._evtsreload1.icon 	= conf.ANNOTATOR_ICON_REFRESH
		self._evtsreload2.icon 	= conf.ANNOTATOR_ICON_REFRESH
		
		self._progress.hide()
		self._radius.hide()
		self._color.hide()
		self.__check_areatab_event()

	###########################################################################
	### UTILS #################################################################
	###########################################################################
	
	def __reload_events(self):
		"""
		Find all the events available on the timeline
		"""
		timeline = self.parent().timeline
		rows 	 = timeline.rows

		events 	 = {}
		for row in rows:
			for event in row.events:
				events[event.title] = True

		events = sorted(events.keys())

		loaded_events = dict(self._drawevents.items)
		self._drawevents.value = [(e, loaded_events.get(e, False)) for e in events]
		
		loaded_events = dict(self._splitevents.items)
		self._splitevents.value = [(e, loaded_events.get(e, False)) for e in events]

	
	###########################################################################
	### EVENTS ################################################################
	###########################################################################

	def show(self):
		"""
		Load the events when the window is oppened
		"""
		super(VideosExporterGui, self).show()
		self.__reload_events()

	def __check_areatab_event(self):
		"""
		Activate or deactivate the color tab
		"""
		if len(list(self._panel_area.value.datasets))>0 or self._usefixedsize.value:
			self._toolbox.set_item_enabled(2, True)
		else:
			self._toolbox.set_item_enabled(2, False)


	def __usefixedcolor_changed_event(self):
		if self._usefixedcolor.value:
			self._color.show()
			self._panel_colors.hide()
		else:
			self._color.hide()
			self._panel_colors.show()


	def __usefixedsize_changed_event(self):
		self.__check_areatab_event()
		if self._usefixedsize.value:
			self._radius.show()
			self._panel_area.hide()
		else:
			self._radius.hide()
			self._panel_area.show()

	def outputfile_changed_event(self):
		"""
		Update the output filename
		"""
		filename = self._outfile.value

		video = self._panel_path.value.selected_video
		if video is not None:
			filename 					   = filename if len(filename)>0 else video.filename
			videofilepath, video_extension = os.path.splitext(video.filename)
			outfilepath, outfile_extension = os.path.splitext(filename)

			names = [outfilepath] if len(outfilepath)>0 else []

			if '{videoindex}' not in outfilepath:   names.append('{videoindex}')
			if len(list(self._splitevents.value))>0:
				if '{event}' not in outfilepath: names.append('{event}')
				if '{start}' not in outfilepath: names.append('{start}')
				if '{end}' not in outfilepath:   names.append('{end}')


			self._outfile.value = ('-'.join(names)+video_extension)
			self._apply.enabled = True			
		else:
			self._apply.enabled = False

	def __video_selection_changed_event(self):
		"""
		Activate the video preview
		"""
		video = self._panel_path.value.selected_video
		if video is not None:
			self._player.value = video.video_capture


	def get_object_area(self, path, areas, index):
		try:
			if self._usefixedsize.value:
				area = (self._radius.value**2*math.pi)
			elif len(areas)>0:
				a = areas[0]
				if isinstance(a, Value ):
					area = a.get_value(index)
				else:
					area = a.get_area_value(index)				
			else:
				area = path.get_area_value(index)
			
			return area
		except:
			return None


	def get_object_color(self, path, colors, index):
		try:
			if self._usefixedcolor.value:
				color = tuple(eval(self._color.value))
			elif len(colors)>0:
				color = colors[0].get_color_avg(index)				
			else:
				color = path.get_color_avg(index)
			if color is None: raise Exception()
		except:
			color = 255,255,255
		return color


	


if __name__ == '__main__': pyforms.start_app(VideosExporterGui)
