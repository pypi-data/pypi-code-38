from confapp import conf
from AnyQt.QtGui import QIcon

from pybpodgui_plugin_waveplayer.module_gui import WavePlayerModuleGUI

class ProjectsWavePlayer(object):

	def register_on_main_menu(self, mainmenu):
		super().register_on_main_menu(mainmenu)

		if len([m for m in mainmenu if 'Tools' in m.keys()]) == 0:
			mainmenu.append({'Tools': []})

		menu_index = 0
		for i, m in enumerate(mainmenu):
			if 'Tools' in m.keys(): menu_index=i; break

		mainmenu[menu_index]['Tools'].append( '-' )	
		mainmenu[menu_index]['Tools'].append( {'Wave player': self.open_waveplayer_plugin, 'icon': None})
	
	def open_waveplayer_plugin(self):
		if not hasattr(self, 'rotaryencoder_plugin'):
			self.waveplayer_plugin = WavePlayerModuleGUI(self)
			self.waveplayer_plugin.show()
			#self.rotaryencoder_plugin.resize(*conf.ROTARYENCODER_PLUGIN_WINDOW_SIZE)			
		else:
			self.waveplayer_plugin.show()

		return self.waveplayer_plugin