__version__ 	= "1.0"
__author__ 		= ['Ricardo Ribeiro', 'Sergio Copeto']
__credits__ 	= ['Ricardo Ribeiro', "Sergio Copeto"]
__license__ 	= "Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>"
__maintainer__ 	= ['Ricardo Ribeiro', 'Sergio Copeto']
__email__ 		= ['ricardo.ribeiro@research.fchampalimaud.org', 'sergio.copeto']
__status__ 		= "Development"

from confapp import conf

conf += 'pybpodgui_plugin_waveplayer.settings'

from pybpodgui_plugin_waveplayer.module import WavePlayer as BpodModule