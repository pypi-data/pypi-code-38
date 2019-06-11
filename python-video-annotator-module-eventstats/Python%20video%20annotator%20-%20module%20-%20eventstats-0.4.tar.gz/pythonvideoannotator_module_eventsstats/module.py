from pythonvideoannotator_module_eventsstats.stats import Stats


class Module(object):

	def __init__(self):
		super(Module, self).__init__()

	
		self.mainmenu[1]['Modules'].append(
			{'Events stats':  self.__open_events_statistics_window },			
		)

	def __open_events_statistics_window(self): Stats(self._time, parent_win=self).show()
