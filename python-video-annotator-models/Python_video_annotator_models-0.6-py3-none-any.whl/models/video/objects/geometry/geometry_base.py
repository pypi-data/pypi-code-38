from pythonvideoannotator_models.models.video.objects.video_object import VideoObject
import numpy as np

class GeometryBase(VideoObject):

	def __init__(self, video):
		super(GeometryBase, self).__init__()

		self.name 	= 'geometry({0})'.format(len(video)) if len(video)>0 else 'geometry'
		self._geometry 	= []

		self._video = video
		self._video += self

	######################################################################
	### OBJECT FUNCTIONS #################################################
	######################################################################

	def create_contours(self, object2d):
		if len(self._geometry)==0: return
		contours = object2d.create_contours()
		begin    = 0

		contour = np.int32([self._geometry[0][1]])
		for index in range( int(self._video.total_frames) ):
			contours.set_contour(index, contour)
		
	######################################################################
	### CLASS FUNCTIONS ##################################################
	######################################################################

	def __str__(self): return self.name


	@property
	def geometry(self): return self._geometry
	
	
	
