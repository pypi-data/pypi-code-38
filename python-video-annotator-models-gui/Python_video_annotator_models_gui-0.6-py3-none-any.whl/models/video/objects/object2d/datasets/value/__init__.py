from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.value.value_gui import ValueGUI
from confapp import conf


Value = type(
	'Value',
	tuple(conf.VIDEOANNOTATOR_MODULES.find_class('models.video.objects.object2d.datasets.value.Value') + [ValueGUI]),
	{}
)
