import sys, os, shutil, re, pyforms, numpy as np, cv2
from confapp import conf
from pyforms.basewidget	 import BaseWidget
from pyforms.controls 	 import ControlDir
from pyforms.controls 	 import ControlPlayer
from pyforms.controls 	 import ControlButton
from pyforms.controls 	 import ControlNumber
from pyforms.controls 	 import ControlSlider
from pyforms.controls 	 import ControlList
from pyforms.controls 	 import ControlCheckBox
from pyforms.controls 	 import ControlText
from pyforms.controls 	 import ControlCheckBoxList
from pyforms.controls 	 import ControlEmptyWidget
from pyforms.controls 	 import ControlProgress
from pyforms.controls 	 import ControlTree

if conf.PYFORMS_MODE=='GUI':
    from AnyQt import QtCore
    from AnyQt.QtWidgets import QMessageBox

from pythonvideoannotator_models.models.video.objects.object2d.datasets.value import Value

class ExportWindow(BaseWidget):

	def __init__(self, parent=None):
		BaseWidget.__init__(self, 'Export data', parent_win=parent)

		self.set_margin(5)			
		self.setMinimumHeight(600)
		self.setMinimumWidth(800)

		self._tree			= ControlTree('Data')
		self._apply  		= ControlButton('Apply', checkable=True)
		self._progress 		= ControlProgress('Progress')
		self._add	    	= ControlButton('Add')
		self._remove		= ControlButton('Remove')
		self._export_list 	= ControlList('Columns to export')
	
		self._outdir 		= ControlDir('Output directory')
		self._outfile 		= ControlText('Output file name')

		self._toggleevts	= ControlCheckBox('Split files by events')
		self._splitevents	= ControlCheckBoxList('Events')
		self._evtsreload    = ControlButton('Reload events')
				
		self._formset = [
			[['_add','_tree'],'||', ['_remove','_export_list']],
			'_toggleevts',
			'_evtsreload',
			'_splitevents',
			'_outdir',
			'_outfile',
			'_apply',
			'_progress'
		]
				
		self._add.value 				= self.__add_column_event
		self._remove.value 				= self.__remove_column_event		
		self._apply.value 				= self.__apply_btn_event
		self._evtsreload.value  		= self.__reload_events
		self._outdir.changed_event 		= self.__update_outfile_name_event
		self._outfile.changed_event 	= self.__update_outfile_name_event
		self._toggleevts.changed_event 	= self.__toggleevents_visibility
		self._splitevents.changed_event = self.__update_outfile_name_event
		self._splitevents.selection_changed_event = self.__update_outfile_name_event
		
		self._tree.show_header 	= False
		self._apply.icon 		= conf.ANNOTATOR_ICON_MOTION
		self._evtsreload.icon 	= conf.ANNOTATOR_ICON_REFRESH
		self._add.icon 			= conf.ANNOTATOR_ICON_ADD
		self._remove.icon 		= conf.ANNOTATOR_ICON_REMOVE

		self._progress.hide()
		self._splitevents.hide()
		self._evtsreload.hide()
		self._apply.enabled = False
		
		self._properties = []

		
	###########################################################################
	### EVENTS ################################################################
	###########################################################################

	def __toggleevents_visibility(self):
		if self._toggleevts.value:
			self._splitevents.show()
			self._evtsreload.show()
		else:
			self._splitevents.hide()
			self._evtsreload.hide()


	def __field_full_name(self, tree_item):
		name = tree_item.text(0)
		while True:
			tree_item = tree_item.parent()
			if tree_item is None: break
			name = "{0} > {1}".format( tree_item.text(0) , name )
		return name

	def __add_column_event(self):
		self.__update_outfile_name_event()
		item = self._tree.selected_item

		if item is None:
			return

		if hasattr(item, 'data_function'):
			self._export_list += [ self.__field_full_name(item) ]
			self._properties.append( (len(item.win), item.data_function) )
		elif isinstance(item.win, Value):
			self._export_list += [ self.__field_full_name(item) ]
			self._properties.append( (len(item.win), item.win.get_value) )

	def __remove_column_event(self):
		self.__update_outfile_name_event()
		if self._export_list.selected_row_index is None:
			return
		elif self._export_list.selected_row_index>=0:
			self._properties.pop(self._export_list.selected_row_index)
			self._export_list -= -1
		
	def __update_outfile_name_event(self):
		"""
		Update the output filename
		"""
		filename = self._outfile.value
		if len(filename.strip())==0: return

		outfilepath, outfile_extension = os.path.splitext(filename)
		names = [outfilepath] if len(outfilepath)>0 else []

		if len(list(self._splitevents.value))>0:
			if '{event}' not in outfilepath: names.append('{event}')
			if '{start}' not in outfilepath: names.append('{start}')
			if '{end}' not in outfilepath:   names.append('{end}')

		self._outfile.value = ('-'.join(names)+'.csv')
		self._apply.enabled = True
			
	def __apply_btn_event(self):

		if self._apply.checked:

			if len(self._properties)==0:
				QMessageBox.about(self, "Error", "You need to select at least one value to export.")
				self._apply.checked = False
				return

			if self._outfile.value is None or len(self._outfile.value.strip())==0: 
				QMessageBox.about(self, "Error", "You need to select the name of the output file.")
				self._apply.checked = False
				return

			if self._outdir.value is None or len(self._outdir.value)==0: 
				QMessageBox.about(self, "Error", "You need to select the name of the output directory.")
				self._apply.checked = False
				return


			self.__update_outfile_name_event()

			self._export_list.enabled 	= False
			self._tree.enabled 			= False
			self._add.enabled 			= False
			self._remove.enabled 		= False
			self._outdir.enabled 		= False
			self._outfile.enabled 		= False
			self._apply.label 			= 'Cancel'

			### calculate the video cuts #############################
			timeline   = self.parent().timeline

			selected_events = self._splitevents.value
			videocuts   = []
			if len(selected_events):
				# use the events to cut the video
				totalframes = 0
				for row in timeline.rows:
					for event in row.events:
						if event.title not in selected_events: continue
						b = event.begin
						e = event.end
						totalframes += e-b
						videocuts.append( (int(b), int(e), event.title) )
				videocuts = sorted(videocuts, key = lambda x: x[0])
			else:
				# no events were selected
				end = max([size for size, func in self._properties])
				totalframes = end
				videocuts   = [(0, int(end), None)]
			##########################################################

			self._progress.min = 0
			self._progress.max = totalframes
			self._progress.show()

			for b, e, eventname in videocuts:

				filename = self._outfile.value
				filename = filename.format(event=eventname, start=b, end=e)
				filename = os.path.join( self._outdir.value, filename)

				with open(filename, 'w') as out:

					## write the csv columns headers
					out.write('frame;')
					for values in self._export_list.value:
						out.write(('{0};'.format(values[0])) )
					out.write('\n')

					## write the values
					for index in range(b, e):
						out.write('{0};'.format(index))
						for _, func in self._properties:
							out.write( '{0};'.format(func(index)))
						out.write( '\n')
						self._progress += 1
							
			
			self._export_list.enabled 	= True
			self._tree.enabled 			= True
			self._add.enabled 			= True
			self._remove.enabled 		= True
			self._outdir.enabled 		= True
			self._outfile.enabled 		= True
			self._apply.label 		= 'Apply'
			self._apply.checked 	= False
			self._progress.hide()

	def __copy_tree_node(self, item, new_item):
		new_item.win = item.win
		if hasattr(item,'data_function'): new_item.data_function = item.data_function

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

		loaded_events = dict(self._splitevents.items)
		self._splitevents.value = [(e, loaded_events.get(e, False)) for e in events]

	@property
	def project(self): return self._project
	@project.setter 
	def project(self, value): 
		self._project = value
		self._tree.clear()
		self._tree.clone_tree( value.tree, copy_function=self.__copy_tree_node )
		self.__reload_events()
		




	

if __name__ == "__main__": pyforms.start_app(ExportWindow)