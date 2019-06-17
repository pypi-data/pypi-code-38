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
## @brief Single argument class. It permit to define the getted argument.
##
class ArgElement:
	##
	## @brief Contructor.
	## @param[in] self Class handle
	## @param[in] option (string) Option name (write in fullmode ex: '--verbose' even if user write '-v')
	## @param[in] value (string) Writed value by the user (defult '')
	##
	def __init__(self, option, value=""):
		self.option = option;
		self.arg = value;
	
	##
	## @brief Get the name of the argument: (write in fullmode ex: '--verbose' even if user write '-v')
	## @param[in] self Class handle
	## @return (string) The argument name
	##
	def get_option_name(self):
		return self.option
	
	##
	## @brief Get argument data set by the user
	## @param[in] self Class handle
	## @return (string) The argument value
	##
	def get_arg(self):
		return self.arg
	
	##
	## @brief Display the Argument property
	## @param[in] self Class handle
	##
	def display(self):
		if len(self.arg) == 0:
			debug.info("option : " + self.option)
		elif len(self.option) == 0:
			debug.info("element :       " + self.arg)
		else:
			debug.info("option : " + self.option + ":" + self.arg)
