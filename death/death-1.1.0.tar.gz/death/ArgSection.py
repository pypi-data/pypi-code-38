#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license MPL v2.0 (see license file)
##
import sys
from realog import debug

##
## @brief Section Class definition (permit to add a comment when requesting help
##
class ArgSection:
	##
	## @brief Constructor
	## @param[in] self Class handle
	## @param[in] sectionName (string) Name of the cestion ex: "option" is displayed [option]
	## @param[in] desc (string) Comment assiciated with the group
	##
	def __init__(self,
	             sectionName="",
	             desc=""):
		self.section = sectionName;
		self.description = desc;
	
	def is_parsable(self):
		return False
	
	##
	## @brief Compatibility with @ref ArgDefine class
	## @param[in] self Class handle
	## @return empty string
	##
	def get_option_small(self):
		return ""
	
	##
	## @brief Compatibility with @ref ArgDefine class
	## @param[in] self Class handle
	## @return empty string
	##
	def get_option_big(self):
		return ""
	
	##
	## @brief get property print value with the correct writing mode
	## @param[in] self Class handle
	## @return String to display in the short line help
	##
	def get_porperties(self):
		color = debug.get_color_set()
		return " [" + color['blue'] + self.section + color['default'] + "]"
	
	##
	## @brief Display the argument property when user request help
	## @param[in] self Class handle
	##
	def display(self):
		color = debug.get_color_set()
		print("	[" + color['blue'] + self.section + color['default'] + "] : " + self.description)

