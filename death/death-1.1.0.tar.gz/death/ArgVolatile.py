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
## @brief Declare an argument value and store it in a parameter
##
class ArgVolatile:
	##
	## @brief Contructor.
	## @param[in] self Class handle
	## @param[in] dest_option (string) Where to store the option name
	## @param[in] optionnal (bool) this element can be not present
	## @param[in] desc (string) user friendly description with this parameter (default "")
	##
	def __init__(self,
	             dest_option="",
	             optionnal=False,
	             desc=""):
		self.dest_option = dest_option;
		if dest_option == "":
			debug.error("volatil argument must be store in an argument name")
		self.optionnal = optionnal;
		self.description = desc;
		self.count = 0;
	
	def is_parsable(self):
		return False
	##
	## @brief Get the small name of the option ex: '-v'
	## @param[in] self Class handle
	## @return (string) Small name value
	##
	def get_option_small(self):
		return ""
	
	##
	## @brief Get the big name of the option ex: '--verbose'
	## @param[in] self Class handle
	## @return (string) Big name value
	##
	def get_option_big(self):
		return self.dest_option
	
	##
	## @brief Get the status of getting user parameter value
	## @param[in] self Class handle
	## @return True The user must write a value
	## @return False The user must NOT write a value
	##
	def need_parameters(self):
		if self.count == 0:
			self.count += 1
			return True
		return False
	
	##
	## @brief Compatibility with @ref ArgSection class
	## @param[in] self Class handle
	## @return (string) empty string
	##
	def get_porperties(self):
		return " [" + self.dest_option + "]"
	
	##
	## @brief Check if the user added value is correct or not with the list of availlable value
	## @param[in] self Class handle
	## @param[in] argument (string) User parameter value (string)
	## @return True The parameter is OK
	## @return False The parameter is NOT Availlable
	##
	def check_availlable(self, argument):
		return True
	
	##
	## @brief Display the argument property when user request help
	## @param[in] self Class handle
	##
	def display(self):
		color = debug.get_color_set()
		print("		" + color['red'] + "[" + self.dest_option + "]" + color['default'])
		if self.optionnal == True:
			print("(OPTIONNAL)")
		if self.description != "":
			print("			" + self.description)
