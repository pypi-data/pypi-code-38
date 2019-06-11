from confapp import conf
from pythonvideoannotator_models_gui.models.project_gui import ProjectGUI

Project = type(
	'Project',
	tuple(conf.VIDEOANNOTATOR_MODULES.find_class('models.Project') + [ProjectGUI]),
	{}
)
