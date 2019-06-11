import os, cv2
from send2trash import send2trash
from pythonvideoannotator_models.models.video.objects.note.note_base import NoteBase

class NoteIO(NoteBase):

	FACTORY_FUNCTION = 'create_note'

	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################

	def save(self, data, note_path):
		data = super(NoteIO, self).save(data, note_path)

		filepath = os.path.join(note_path, 'note.txt')
		
		with open(filepath, 'w') as outfile: 
			outfile.write((self.note))

		return data

	def load(self, data, note_path):
		data = super(NoteIO, self).load(data, note_path)

		filepath = os.path.join(note_path, 'note.txt')
		with open(filepath, 'r') as infile: 
			self.note = infile.read()
	
		return data