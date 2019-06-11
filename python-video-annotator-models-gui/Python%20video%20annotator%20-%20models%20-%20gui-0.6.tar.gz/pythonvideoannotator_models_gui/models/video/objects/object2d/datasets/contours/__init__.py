from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours.contours_gui import ContoursGUI
from confapp import conf


Contours = type(
	'Contours',
	tuple(conf.VIDEOANNOTATOR_MODULES.find_class('models.video.objects.object2d.datasets.contours.Contours') + [ContoursGUI]),
	{}
)
