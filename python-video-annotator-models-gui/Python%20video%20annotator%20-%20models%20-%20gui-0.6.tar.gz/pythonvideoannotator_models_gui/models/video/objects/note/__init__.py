from confapp import conf
from pythonvideoannotator_models_gui.models.video.objects.note.note_gui import NoteGUI

Note = type(
	'Note',
	tuple(conf.VIDEOANNOTATOR_MODULES.find_class('models.video.objects.note.Note') + [NoteGUI]),
	{}
)
