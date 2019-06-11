import csv, cv2, os, numpy as np
from confapp import conf

class MotionDataset(object):

	def __init__(self, object2d):
		super(MotionDataset, self).__init__(object2d)
		self._motion = []
		
	def create_motion_tree_nodes(self):
		self.create_data_node('motion', icon=conf.ANNOTATOR_ICON_MOTION)

	def get_motion_value(self, index): return self.get_motion(index)
		
	def get_motion(self, index):
		if index<0 or index>=len(self._motion): return None
		return self._motion[index]

	def set_motion(self, index, value):
		if len(self._motion)==0: self.create_motion_tree_nodes()
		
		if index>=len(self._motion): 
			for i in range(len(self._motion), index+1): self._motion.append(None)
		self._motion[index] = value



	def save(self, data, datasets_path=None):
		data = super(MotionDataset, self).save(data, datasets_path)
		dataset_path = self.directory

		motion_file = os.path.join(dataset_path, 'motion.csv')
		with open(motion_file, 'wb') as outfile:
			outfile.write((';'.join(['frame','motion'])+'\n' ).encode( ))
			for index in range(len(self)):
				motion = self.get_motion(index)
				row = [index] + [motion]
				outfile.write((';'.join( map(str,row) )).encode( ))
				outfile.write(b'\n')

		return data

	def load(self, data, dataset_path=None):
		super(MotionDataset, self).load(data, dataset_path)
		motion_file = os.path.join(dataset_path, 'motion.csv')
		
		if os.path.exists(motion_file):
			with open(motion_file, 'r') as infile:
				infile.readline()
				for i, line in enumerate(infile):
					csvrow = line[:-1].split(';')
					
					frame 	= int(csvrow[0])
					motion 	= float(csvrow[1]) if csvrow[1] is not None and csvrow[1]!='None' else None
					
					self.set_motion(frame, motion)