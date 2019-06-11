import os
from confapp import conf
from send2trash import send2trash
from AnyQt import QtCore
from pythonvideoannotator_models.utils import tools
from pythonvideoannotator.utils.tools import list_files_in_path

class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()
		self._update_time = True  # Use to avoid double video jump 2 frame trigger

		self.mainmenu[2]['Windows'].append({'Timeline': self.__show_timeline_event, 'icon':conf.PYFORMS_ICON_EVENTTIMELINE_TIMELINE })
		

	def __show_timeline_event(self):
		self._dock.show()

	def init_form(self):
		self._time.pointer_changed_event = self.__time_changed
		super(Module, self).init_form()

	######################################################################################
	#### EVENTS ##########################################################################
	######################################################################################


	def __time_changed(self):
		"""
		If the timeline pointer is changed the player position is also changed
		"""
		if self._player.value is None: return

		# Flag to avoid recursive position change, between the player and the timeline
		self._update_time = False        
		self._player.video_index = self._time.value
		self._player.call_next_frame()
		self._update_time = True

	def __dummy(self): pass

	def process_frame_event(self, frame):

		if self._update_time and self._player.value:

			# Update the pointer in the timeline
			self._time.pointer_changed_event = self.__dummy
			self._time.value = self._player._current_frame_index
			self._time.pointer_changed_event = self.__time_changed
				
		return super(Module, self).process_frame_event(frame)



	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	
	def save(self, data, project_path=None):
		data = super(Module,self).save(data, project_path)
		graphs_path = os.path.join(project_path, 'graphs')
		if not os.path.exists(graphs_path): os.makedirs(graphs_path)

		graphs = []
		for graph in self._time.graphs:
			graph_path = os.path.join(graphs_path, graph.name+'.csv')
			graph.export_2_file(graph_path)
			graphs.append(graph_path)


		for path in tools.list_files_in_path(graphs_path):
			if path not in graphs: send2trash(path)

		return data

	def load(self, data, project_path=None):
		graphs_path = os.path.join(project_path, 'graphs')

		for graph_path in list_files_in_path(graphs_path):
			try:
				self._time.import_graph_csv(graph_path, ignore_rows=1)
			except:
				print("Could not load", graph_path)
		super(Module,self).load(data, project_path)
		
