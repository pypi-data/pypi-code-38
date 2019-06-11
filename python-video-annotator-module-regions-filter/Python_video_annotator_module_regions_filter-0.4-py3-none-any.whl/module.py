import cv2
from confapp import conf
from pythonvideoannotator_module_regionsfilter.regions_filter import RegionsFilter


class Module(object):

	def __init__(self):
		"""
		This implements the Path edition functionality
		"""
		super(Module, self).__init__()
		self.regions_filter = RegionsFilter(self)

		self.mainmenu[1]['Modules'].append(
			{'Filter by regions': self.regions_filter.show, 'icon':conf.ANNOTATOR_ICON_REGIONS },			
		)

	def video_changed_event(self):
		super(Module, self).video_changed_event()
		self.regions_filter.video_filename = self._video.value

	def add_event_2_timeline(self, track, evt_name, begin, end):
		self._time.add_event( begin, end, evt_name, track )

	def add_dataset_event(self, dataset):
		super(Module, self).add_dataset_event(dataset)
		self.regions_filter.add_dataset_event(dataset)

	def removed_dataset_event(self, dataset):
		super(Module, self).removed_dataset_event(dataset)
		self.regions_filter.removed_dataset_event(dataset)

	def removed_object_event(self, obj):
		super(Module, self).removed_object_event(obj)
		self.regions_filter.removed_object_event(obj)
	

	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	
	def save(self, data, project_path=None):
		data = super(Module, self).save(data, project_path)
		data['regions-filter-settings'] = self.regions_filter.save({})
		return data

	def load(self, data, project_path=None):
		super(Module, self).load(data, project_path)
		if 'regions-filter-settings' in data: 
			self.regions_filter.load( data['regions-filter-settings'] )
		