from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path.path_gui import PathGUI
from confapp import conf


Path = type(
	'Path',
	tuple(conf.VIDEOANNOTATOR_MODULES.find_class('models.video.objects.object2d.datasets.path.Path') + [PathGUI]),
	{}
)
