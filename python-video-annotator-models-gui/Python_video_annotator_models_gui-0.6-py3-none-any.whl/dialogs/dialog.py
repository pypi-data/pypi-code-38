
class Dialog(object):

	instantiated_dialogs = []
	project 			 = None

	def __init__(self):
		self.instantiated_dialogs.append(self)

		
		for video in self.project.videos:
			self += video

	def destroy(self, destroyWindow = True, destroySubWindows = True):
		super(Dialog, self).destroy(destroyWindow, destroySubWindows)
		self.instantiated_dialogs.remove(self)

	