#! /usr/bin/python2
# -*- coding: utf-8 -*-
from pythonvideoannotator_models.models.imodel import IModel
from pythonvideoannotator_models.models.video import Video

class ProjectBase(IModel):

	def __init__(self):
		super(IModel, self).__init__()

		self._videos 	= []
		self._directory = None

	######################################################################################
	#### FUNCTIONS #######################################################################
	######################################################################################

	def __add__(self, obj):
		if isinstance(obj, Video): self._videos.append(obj)
		return self

	def __sub__(self, obj):
		if isinstance(obj, Video): self._videos.remove(obj)
		return self
		

	def create_video(self): return Video(self)

	def find_video(self, name):
		for o in self.videos:
			if o.name == name: return o
		return None

	######################################################################################
	#### PROPERTIES ######################################################################
	######################################################################################

	@property
	def videos(self): return self._videos
	@videos.setter
	def videos(self, value): self._videos = value

	@property
	def directory(self): return self._directory