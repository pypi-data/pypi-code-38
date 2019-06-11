#! /usr/bin/python2
# -*- coding: utf-8 -*-
import os,simplejson as  json
from confapp import conf
from send2trash import send2trash
from pythonvideoannotator_models.utils import tools

from pythonvideoannotator_models.models.video.video_base import VideoBase

class VideoIO(VideoBase):

	######################################################################################
	#### IO FUNCTIONS ####################################################################
	######################################################################################
	
	def save(self, data, videos_path=None):
		video_path = os.path.join(videos_path, self.name)
		if not os.path.exists(video_path): os.makedirs(video_path)

		############## save objects #############
		objects_path = os.path.join(video_path, 'objects')
		if not os.path.exists(objects_path): os.makedirs(objects_path)
		for obj in self._childrens: 
			obj_path = os.path.join(objects_path, obj.name)
			if not os.path.exists(obj_path): os.makedirs(obj_path)
			obj.save({}, obj_path)
		# remove not used objects ###############
		objects_paths = [os.path.join(objects_path, obj.name) for obj in self._childrens]
		for obj_path in tools.list_folders_in_path(objects_path):
			if obj_path not in objects_paths: send2trash(obj_path)
		#########################################

		videoconf = os.path.join(video_path, 'video.json')
		data['video-filepath'] = os.path.relpath(self.filepath, start=self.project.directory)
		with open(videoconf, 'w') as outfile:
			json.dump(data, outfile)

		return data




	def load(self, data, video_path=None):
		videoconf = os.path.join(video_path, 'video.json')
		
		with open(videoconf, 'r') as outfile:
			data = json.load(outfile)
		self.filepath = os.path.join(self.project.directory ,data['video-filepath'])

		objects_path = os.path.join(video_path, 'objects')
		objects_dirs = tools.list_folders_in_path(objects_path)

		for obj_dir in objects_dirs:
			name		= os.path.basename(obj_dir)
			conf_path 	= os.path.join(obj_dir, 'dataset.json')
			with open(conf_path, 'r') as infile:
				dataset_conf 	= json.load(infile)
				func 			= getattr(self, dataset_conf['factory-function'])
				dataset 		= func()
				dataset.load(dataset_conf, obj_dir)
				dataset.name    = name

		super(VideoIO, self).load(data, video_path)