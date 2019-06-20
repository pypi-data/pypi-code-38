# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 13:54:03 2019

@author: Cristian Vargas, Lukasz Kaczmarek, and Rodolfo Ferro
"""

import os, os.path

from utils import dehaze, gamma, kernel, clahe
import matplotlib.pyplot as plt
import numpy
import wget
import cv2


class PipeItem(object):
    
    def __init__(self, item, **kwargs):
        self.item = item
        self.kwargs = kwargs
        
    def run(self, image):
        return self.item(image, **self.kwargs)


class Pipeline(object):
	
	def __init__(self, pipeline=[]):
		
		self.images = []
		self.pipeline = pipeline
		self.outputPath = ''
		self.inputPath = ''
		self.outputFIleType = 'jpg'
	
	def setOutputFileType(self, fileType='jpg'):
		
		if fileType in ('jpg', 'jpeg', 'png', 'tif'):
			self.outputFIleType = fileType
		else:
			print("File type must be jpg, jpeg, png or tif")
			
	def setOutputPath(self, path):
		self.outputPath = path
		if not os.path.isdir(self.outputPath):
			try:
				os.mkdir(self.outputPath)
			except IOError as error:
				print(error)
		
	
	def addImage(self, imagePath):
		self.images.append(imagePath)

	def addInputFolder(self, path):
		self.inputPath = path
		for root, dir, files in os.walk(self.inputPath):
			for name in files:
				extension = name.split('.')[-1]
				if extension in ['jpg', 'jpeg', 'png', 'tif']:
					self.addImage(os.path.join(root, name))
	
	def addPipeItem(self, item):
		self.pipeline.append(item)
	
	
	def setPipeline(self, pipeline):
		self.pipeline = pipeline
		
	def saveModified(self, image, fileName):
		
		filename = ''.join(fileName.split('.')[:-1])
		outputPath = os.path.join(self.outputPath,filename+"_modified."+self.outputFIleType)
		try:
			cv2.imwrite( outputPath, image )
		except IOError as error:
			print(error)
			
	def show(self, image):
		plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
		plt.show()
	
	def process(self, image, display_steps=False):
	
		if isinstance(image, str):
			try:
				temp = cv2.imread(image)
			except IOError as error:
				print(error)	
		elif isinstance(image, numpy.ndarray):
			temp = image
			 
		for item in self.pipeline:
			if display_steps:
				self.show(temp)
				
			temp = item.run(temp)
			
		if display_steps:
			self.show(temp)
			
		return temp
	
	def run(self, save_files=True, display_steps=False):
		
		number = len(self.images)
		current = 0
		for image in self.images:
			current += 1
			print("Processing image ", current, "out of", number, "\n", image)
			temp = self.process(image, display_steps=display_steps)
		
			if save_files:
				fileName = os.path.split(image)[1]
				self.saveModified(temp, fileName)


def example():
	"""TODO. Example function.
	"""
	img_url = "https://rodolfoferro.xyz/assets/images/dog_original.jpeg"
	wget.download(img_url, out='dog.jpg')
	cwd = os.getcwd()
	
	filter_sequence = [
		PipeItem(dehaze),
		PipeItem(gamma, gamma=1.8),
		PipeItem(kernel, kernel=[[-1,-1,-1],[-1,20,-1],[-1,-1,-1]]),
		PipeItem(clahe)
	]

	pipeline = Pipeline()
	print(cwd)
	pipeline.addInputFolder(cwd)
	pipeline.setOutputPath(cwd)
	pipeline.setOutputFileType('jpg')
	pipeline.setPipeline(filter_sequence)	
	pipeline.run(save_files=True, display_steps=False)


if __name__ == "__main__":
	example()
