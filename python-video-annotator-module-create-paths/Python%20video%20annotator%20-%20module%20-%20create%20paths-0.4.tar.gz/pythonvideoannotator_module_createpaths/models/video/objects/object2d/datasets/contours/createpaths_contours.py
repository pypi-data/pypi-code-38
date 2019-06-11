from confapp import conf
import cv2, numpy as np, os
import base64
from pythonvideoannotator.utils.tools import make_lambda_func

class CreatePathsContours(object):

	def __init__(self, name=None):
		super(CreatePathsContours, self).__init__(name)

		
	######################################################################
	### EVENTS ###########################################################
	######################################################################
	
	def create_tree_nodes(self):
		super(CreatePathsContours,self).create_tree_nodes()

		LABEL = 'Create path from the property'
		
		self.tree.add_popup_menu_option(
			label=LABEL,
			function_action=make_lambda_func(
				self.__create_path, 
				x_function=self.get_position_x_value, 
				y_function=self.get_position_y_value
			), 
			item=self.treenode_position, icon=conf.ANNOTATOR_ICON_PATH
		)
		self.tree.add_popup_menu_option(
			label=LABEL,
			function_action=make_lambda_func(
				self.__create_path, 
				x_function=self.get_position_x_value, 
				y_function=self.get_position_y_value
			), 
			item=self.treenode_boundingrect, icon=conf.ANNOTATOR_ICON_PATH
		)
		self.tree.add_popup_menu_option(
			label=LABEL,
			function_action=make_lambda_func(
				self.__create_path, 
				x_function=self.get_fitellipse_centerx_value, 
				y_function=self.get_fitellipse_centery_value
			), 
			item=self.treenode_fitellipse, icon=conf.ANNOTATOR_ICON_PATH
		)
		self.tree.add_popup_menu_option(
			label=LABEL,
			function_action=make_lambda_func(
				self.__create_path, 
				x_function=self.get_extremepoints_p1_x_value, 
				y_function=self.get_extremepoints_p1_y_value
			), 
			item=self.treenode_extremepoints_p1, icon=conf.ANNOTATOR_ICON_PATH
		)
		self.tree.add_popup_menu_option(
			label=LABEL,
			function_action=make_lambda_func(
				self.__create_path, 
				x_function=self.get_extremepoints_p2_x_value, 
				y_function=self.get_extremepoints_p2_y_value
			), 
			item=self.treenode_extremepoints_p2, icon=conf.ANNOTATOR_ICON_PATH
		)

	def __create_path(self, x_function, y_function):
		obj2d 	= self.object2d
		path 	= obj2d.create_path()
		for index in range(len(self)):
			x = x_function(index)
			y = y_function(index)
			path.set_position(index, x, y)