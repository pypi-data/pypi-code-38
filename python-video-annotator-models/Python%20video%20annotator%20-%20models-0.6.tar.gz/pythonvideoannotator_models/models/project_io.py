#! /usr/bin/python2
# -*- coding: utf-8 -*-
import os, simplejson as json
from confapp import conf
from send2trash import send2trash
from pythonvideoannotator_models.utils import tools
from pythonvideoannotator_models.models.project_base import ProjectBase

class ProjectIO(ProjectBase):

	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################
	
	def save(self, data={}, project_path=None):
		project_path = str(project_path) if project_path is not None else self.directory
		if project_path is None: raise Exception('The project path is not defined')

		self._directory = str(project_path)

		videos_path = os.path.join(project_path, 'videos')
		if not os.path.exists(videos_path): os.makedirs(videos_path)

		data['videos'] = []

		## Save videos #################################
		videos_paths = []
		for video in self.videos:
			data['videos'].append(video.save({}, videos_path))
			videos_paths.append(video.directory)

		## Check if there are videos in the videos folder that should be removed		
		for video_path in tools.list_folders_in_path(videos_path):
			if video_path not in videos_paths: send2trash(video_path)

		

		#Save the project file ######################################
		project_filename = os.path.join(self.directory, 'project.json')
		with open(project_filename, 'w') as outfile: 
			json.dump(data, outfile)

		return data




	def load(self, data, project_path=None):

		project_path = str(project_path) if project_path is not None else self.directory
		if project_path is None: raise Exception('The project path was not defined')

		self._directory = os.path.abspath(project_path)

		project_filename = os.path.join(str(project_path), 'project.json')
		with open(project_filename, 'r') as outfile:
			data.update( json.load(outfile) )
	
		videos_path  = os.path.join(project_path, 'videos')		
		videos_paths = tools.list_folders_in_path(videos_path)

		for video_path in videos_paths:
			video = self.create_video()
			video.load(data, video_path)

		
		
		return data